package org.fog.test.perfeval;

import java.io.*;
import java.util.*;

import org.apache.commons.math3.util.Pair;
import org.cloudbus.cloudsim.CloudletSchedulerSpaceShared;
import org.cloudbus.cloudsim.Cloudlet;
import org.cloudbus.cloudsim.ResCloudlet;
import org.cloudbus.cloudsim.Host;
import org.cloudbus.cloudsim.Log;
import org.cloudbus.cloudsim.Pe;
import org.cloudbus.cloudsim.Storage;
import org.cloudbus.cloudsim.UtilizationModelFull;
import org.fog.scheduler.StreamOperatorScheduler;
import org.cloudbus.cloudsim.core.CloudSimTags;
import org.cloudbus.cloudsim.core.CloudSim;
import org.cloudbus.cloudsim.core.SimEvent;
import org.cloudbus.cloudsim.core.predicates.PredicateType;
import org.cloudbus.cloudsim.power.PowerHost;
import org.cloudbus.cloudsim.provisioners.BwProvisionerSimple;
import org.cloudbus.cloudsim.provisioners.PeProvisionerSimple;
import org.cloudbus.cloudsim.provisioners.RamProvisionerSimple;
import org.fog.application.AppEdge;
import org.fog.application.AppLoop;
import org.fog.application.AppModule;
import org.fog.application.Application;
import org.fog.application.selectivity.FractionalSelectivity;
import org.fog.application.selectivity.SelectivityModel;
import org.fog.entities.Actuator;
import org.fog.entities.FogBroker;
import org.fog.entities.FogDevice;
import org.fog.entities.FogDeviceCharacteristics;
import org.fog.entities.Sensor;
import org.fog.entities.Tuple;
import org.fog.placement.Controller;
import org.fog.placement.ModuleMapping;
import org.fog.placement.ModulePlacementMapping;
import org.fog.policy.AppModuleAllocationPolicy;
import org.fog.utils.Config;
import org.fog.utils.FogEvents;
import org.fog.utils.FogLinearPowerModel;
import org.fog.utils.FogUtils;
import org.fog.utils.NetworkUsageMonitor;
import org.fog.utils.TimeKeeper;
import org.fog.utils.distribution.DeterministicDistribution;
import org.fog.utils.distribution.Distribution;

/**
 * Strict controlled validation of the queueing-aware fogonomics model in iFogSim2.
 *
 * The validation mode is intentionally aligned with the analytical assumptions:
 *   - one aggregate source per provider;
 *   - Poisson aggregate arrivals for M/M/1 experiments;
 *   - exponential service demand for M/M/1 experiments;
 *   - one FCFS server (CloudletSchedulerSpaceShared) per provider at VM/cloudlet level;
 *   - exact next-completion event scheduling (avoids PowerDatacenter interval bias);
 *   - one PE per provider with no PE overbooking; host-level VM scheduling uses the native StreamOperatorScheduler expected by FogDevice;
 *   - provider MIPS = mu * mean_tuple_MI, therefore E[S] = 1/mu;
 *   - network path: Sensor -> access fog -> provider fog -> access fog -> actuator;
 *   - one actuator per provider;
 *   - post-warm-up latency, provider sojourn, queueing, service, network and energy metrics.
 *
 * Why this class exists:
 * the stock iFogSim2 examples use time-shared cloudlet scheduling and overbooking-oriented
 * provisioners. Those are useful for general fog experiments but are not the same service
 * discipline assumed by an FCFS M/M/1 analytical queue. This class removes that mismatch while
 * keeping iFogSim2/CloudSim as the discrete-event, fog-topology and network execution engine.
 *
 * Usage (one row per JVM):
 *   java org.fog.test.perfeval.FogEconomicsIFogSim2StrictMM1V5 \
 *        ifogsim_scenarios_strict_mm1.csv 1 strict_results.csv
 */
public class FogEconomicsIFogSim2StrictMM1V5 {

    private static final List<FogDevice> fogDevices = new ArrayList<FogDevice>();
    private static final List<Sensor> sensors = new ArrayList<Sensor>();
    private static final List<Actuator> actuators = new ArrayList<Actuator>();

    private static InstrumentedFogDevice fogA, fogB;
    private static FogDevice accessA, accessB;
    private static Scenario s;
    private static SpatialStats spatial;

    private static final LatencyStats endToEndA = new LatencyStats();
    private static final LatencyStats endToEndB = new LatencyStats();
    private static final LatencyStats providerSystemA = new LatencyStats();
    private static final LatencyStats providerSystemB = new LatencyStats();
    private static final LatencyStats providerQueueA = new LatencyStats();
    private static final LatencyStats providerQueueB = new LatencyStats();
    // Native VM-level FCFS scheduler diagnostics. These are the queueing metrics used
    // for analytical validation; providerSystemA/B above are retained as an independent
    // wrapper measurement from provider arrival until the result tuple is emitted.
    private static final LatencyStats schedulerSystemA = new LatencyStats();
    private static final LatencyStats schedulerSystemB = new LatencyStats();
    private static final LatencyStats schedulerQueueA = new LatencyStats();
    private static final LatencyStats schedulerQueueB = new LatencyStats();
    private static final LatencyStats schedulerServiceA = new LatencyStats();
    private static final LatencyStats schedulerServiceB = new LatencyStats();
    private static InstrumentedFcfsScheduler fcfsA, fcfsB;
    private static final LatencyStats ingressA = new LatencyStats();
    private static final LatencyStats ingressB = new LatencyStats();
    private static final LatencyStats egressA = new LatencyStats();
    private static final LatencyStats egressB = new LatencyStats();
    private static final Map<Integer, Double> providerDepartureByTuple = new HashMap<Integer, Double>();
    private static final LatencyStats sampledServiceA = new LatencyStats();
    private static final LatencyStats sampledServiceB = new LatencyStats();
    private static final LatencyStats sampledInterarrivalA = new LatencyStats();
    private static final LatencyStats sampledInterarrivalB = new LatencyStats();

    private static final Map<Integer, Double> serviceDemandByTuple = new HashMap<Integer, Double>();

    private static double warmupEnergyA = 0.0;
    private static double warmupEnergyB = 0.0;
    private static double finalEnergyA = 0.0;
    private static double finalEnergyB = 0.0;

    private static final String APP_ID = "fogonomics-strict-mm1";
    private static final String MOD_A = "fog_service_A";
    private static final String MOD_B = "fog_service_B";
    private static final String SEN_A = "TASK_A";
    private static final String SEN_B = "TASK_B";
    private static final String ACT_A = "ACT_A";
    private static final String ACT_B = "ACT_B";
    private static final String OUT_A = "RESULT_A";
    private static final String OUT_B = "RESULT_B";

    // CloudSim 3.0 bundled with iFogSim2 v2.0.0 defaults to 0.1 s.
    // That resolution is too coarse for sub-second queueing validation.
    private static final double EVENT_EPSILON_S = 1.0e-4;

    public static void main(String[] args) {
        Locale.setDefault(Locale.US);
        if (args.length != 3) {
            System.err.println("Usage: FogEconomicsIFogSim2StrictMM1V5 <scenarios.csv> <oneBasedRow> <output.csv>");
            System.exit(2);
        }

        try {
            s = readScenario(args[0], Integer.parseInt(args[1]));
            Config.MAX_SIMULATION_TIME = (int)Math.ceil(s.simulationTimeS);
            run(args[2]);
        } catch (Exception ex) {
            ex.printStackTrace();
            System.exit(1);
        }
    }

    private static void run(String output) throws Exception {
        CloudSim.init(1, Calendar.getInstance(), false, EVENT_EPSILON_S);
        if (s.quiet) Log.disable();

        FogBroker broker = new FogBroker("fogonomics-broker");
        Application app = createApplication(APP_ID, broker.getId());
        app.setUserId(broker.getId());

        createTopology(broker.getId(), APP_ID);

        ModuleMapping map = ModuleMapping.createModuleMapping();
        map.addModuleToDevice(MOD_A, fogA.getName());
        map.addModuleToDevice(MOD_B, fogB.getName());

        ValidationController controller = new ValidationController(
                "fogonomics-controller", fogDevices, sensors, actuators);
        controller.submitApplication(app, new ModulePlacementMapping(fogDevices, app, map));

        TimeKeeper.getInstance().setSimulationStartTime(Calendar.getInstance().getTimeInMillis());

        System.out.println("Running strict validation: " + s.scenario
                + " | arrival=" + s.arrivalMode
                + " | service=" + s.serviceMode
                + " | cloudletScheduler=FCFS"
                + " | hostVmScheduler=StreamOperatorScheduler"
                + " | eventEpsilon=" + EVENT_EPSILON_S
                + " | T=" + s.simulationTimeS
                + " | warmup=" + s.warmupS);

        CloudSim.startSimulation();
        writeResults(output, app);
        System.out.println("Strict validation finished: " + s.scenario);
    }

    private static void createTopology(int userId, String appId) throws Exception {
        spatial = computeSpatialStats(s.xStar, s.densityMode, s.spatialSamples);

        FogDevice cloud = createPlainFogDevice("cloud", 44800, 40000,
                100000, 100000, 0, 0.01, 1648, 1332);
        cloud.setParentId(-1);
        fogDevices.add(cloud);

        final double mipsA = s.muA * s.tupleCpuMI;
        final double mipsB = s.muB * s.tupleCpuMI;

        fogA = createProviderFogDevice("fog-provider-A", "A", MOD_A, ACT_A,
                mipsA, s.fogRamMB, s.uplinkBw, s.downlinkBw, 1,
                s.ratePerMips, s.busyPowerW, s.idlePowerW,
                providerSystemA, providerQueueA, ingressA);
        fogB = createProviderFogDevice("fog-provider-B", "B", MOD_B, ACT_B,
                mipsB, s.fogRamMB, s.uplinkBw, s.downlinkBw, 1,
                s.ratePerMips, s.busyPowerW, s.idlePowerW,
                providerSystemB, providerQueueB, ingressB);

        fogA.setParentId(cloud.getId());
        fogB.setParentId(cloud.getId());
        fogA.setUplinkLatency(0.0);
        fogB.setUplinkLatency(0.0);
        fogDevices.add(fogA);
        fogDevices.add(fogB);

        // Access fog devices are routing-only nodes. No application module is placed here.
        accessA = createPlainFogDevice("access-A", 1000, 1024,
                s.uplinkBw, s.downlinkBw, 2, 0.0, 20.0, 10.0);
        accessB = createPlainFogDevice("access-B", 1000, 1024,
                s.uplinkBw, s.downlinkBw, 2, 0.0, 20.0, 10.0);
        accessA.setParentId(fogA.getId());
        accessB.setParentId(fogB.getId());
        accessA.setUplinkLatency(s.fogLinkLatencyS);
        accessB.setUplinkLatency(s.fogLinkLatencyS);
        fogDevices.add(accessA);
        fogDevices.add(accessB);

        double lambdaA = s.taskRate * s.DA;
        double lambdaB = s.taskRate * s.DB;

        if (lambdaA > 0.0) {
            addAggregateSource(userId, appId, accessA, SEN_A, "A",
                    lambdaA, spatial.avgDistA, s.sigmaA,
                    s.seed + 10007L, s.muA * s.tupleCpuMI,
                    sampledServiceA, sampledInterarrivalA);
        }
        if (lambdaB > 0.0) {
            addAggregateSource(userId, appId, accessB, SEN_B, "B",
                    lambdaB, spatial.avgDistB, s.sigmaB,
                    s.seed + 20011L, s.muB * s.tupleCpuMI,
                    sampledServiceB, sampledInterarrivalB);
        }

        MeasuringActuator a = new MeasuringActuator(
                "actuator-A", userId, appId, ACT_A, endToEndA, egressA, s.warmupS);
        a.setGatewayDeviceId(accessA.getId());
        a.setLatency(s.actuatorLatencyS);
        actuators.add(a);

        MeasuringActuator b = new MeasuringActuator(
                "actuator-B", userId, appId, ACT_B, endToEndB, egressB, s.warmupS);
        b.setGatewayDeviceId(accessB.getId());
        b.setLatency(s.actuatorLatencyS);
        actuators.add(b);
    }

    private static void addAggregateSource(int userId, String appId, FogDevice gateway,
            String sensorType, String suffix, double lambda, double averageDistance,
            double sigma, long seed, double providerMips,
            LatencyStats serviceSamples, LatencyStats interarrivalSamples) throws IOException {

        double meanInterarrival = 1.0 / lambda;
        Distribution arrival = makeDistribution(meanInterarrival, s.arrivalMode,
                seed, s.traceFile, s.traceScale);

        AggregateValidationSensor sensor = new AggregateValidationSensor(
                "aggregate-sensor-" + suffix, sensorType, userId, appId,
                arrival, s.arrivalMode, s.tupleCpuMI, s.serviceMode,
                seed ^ 0x5DEECE66DL, providerMips, serviceSamples, interarrivalSamples);
        sensor.setGatewayDeviceId(gateway.getId());
        sensor.setLatency(s.accessLatencyS + s.tS * (1.0 - sigma) * averageDistance);
        sensors.add(sensor);
    }

    private static Distribution makeDistribution(double mean, String mode, long seed,
            String trace, double scale) throws IOException {
        if ("deterministic".equalsIgnoreCase(mode)) return new DeterministicDistribution(mean);
        if ("poisson".equalsIgnoreCase(mode)) return new ExponentialInterarrival(mean, seed);
        if ("trace".equalsIgnoreCase(mode)) return new TraceInterarrival(trace, mean, scale, seed);
        throw new IllegalArgumentException("Unknown arrival mode: " + mode);
    }

    private static FogDevice createPlainFogDevice(String name, double mips, int ram,
            long upBw, long downBw, int level, double ratePerMips,
            double busyPower, double idlePower) throws Exception {
        return createFogDeviceInternal(name, null, null, mips, ram, upBw, downBw,
                level, ratePerMips, busyPower, idlePower);
    }

    private static InstrumentedFogDevice createProviderFogDevice(String name,
            String providerLabel, String moduleName, String actuatorType,
            double mips, int ram, long upBw, long downBw, int level,
            double ratePerMips, double busyPower, double idlePower,
            LatencyStats systemStats, LatencyStats queueStats, LatencyStats ingressStats) throws Exception {

        HostBundle b = createHostBundle(mips, ram, busyPower, idlePower);
        FogDeviceCharacteristics ch = new FogDeviceCharacteristics(
                "x86", "Linux", "Xen", b.host, 10.0, 3.0, 0.05, 0.001, 0.0);

        InstrumentedFogDevice dev = new InstrumentedFogDevice(
                name, providerLabel, moduleName, actuatorType,
                ch, new AppModuleAllocationPolicy(b.hosts), new LinkedList<Storage>(),
                CloudSim.getMinTimeBetweenEvents(), upBw, downBw, 0.0, ratePerMips, systemStats, queueStats, ingressStats);
        dev.setLevel(level);
        return dev;
    }

    private static FogDevice createFogDeviceInternal(String name,
            String providerLabel, String moduleName, double mips, int ram,
            long upBw, long downBw, int level, double ratePerMips,
            double busyPower, double idlePower) throws Exception {

        HostBundle b = createHostBundle(mips, ram, busyPower, idlePower);
        FogDeviceCharacteristics ch = new FogDeviceCharacteristics(
                "x86", "Linux", "Xen", b.host, 10.0, 3.0, 0.05, 0.001, 0.0);

        FogDevice dev = new FogDevice(
                name, ch, new AppModuleAllocationPolicy(b.hosts), new LinkedList<Storage>(),
                CloudSim.getMinTimeBetweenEvents(), upBw, downBw, 0.0, ratePerMips);
        dev.setLevel(level);
        return dev;
    }

    private static HostBundle createHostBundle(double mips, int ram,
            double busyPower, double idlePower) {
        List<Pe> peList = new ArrayList<Pe>();
        peList.add(new Pe(0, new PeProvisionerSimple(mips)));

        PowerHost host = new PowerHost(
                FogUtils.generateEntityId(),
                new RamProvisionerSimple(ram),
                new BwProvisionerSimple(1000000),
                1000000L,
                peList,
                new StreamOperatorScheduler(peList),
                new FogLinearPowerModel(busyPower, idlePower));

        List<Host> hosts = new ArrayList<Host>();
        hosts.add(host);
        return new HostBundle(host, hosts);
    }

    private static final class HostBundle {
        final PowerHost host;
        final List<Host> hosts;
        HostBundle(PowerHost host, List<Host> hosts) {
            this.host = host;
            this.hosts = hosts;
        }
    }

    @SuppressWarnings("serial")
    private static Application createApplication(String appId, int userId) {
        Application app = Application.createApplication(appId, userId);

        fcfsA = addFcfsModule(app, MOD_A, "A", userId, s.muA * s.tupleCpuMI, 128, s.moduleSize,
                schedulerSystemA, schedulerQueueA, schedulerServiceA);
        fcfsB = addFcfsModule(app, MOD_B, "B", userId, s.muB * s.tupleCpuMI, 128, s.moduleSize,
                schedulerSystemB, schedulerQueueB, schedulerServiceB);

        app.addAppEdge(SEN_A, MOD_A,
                s.tupleCpuMI, s.tupleNetUnits, SEN_A, Tuple.UP, AppEdge.SENSOR);
        app.addAppEdge(SEN_B, MOD_B,
                s.tupleCpuMI, s.tupleNetUnits, SEN_B, Tuple.UP, AppEdge.SENSOR);

        // Direct provider-to-actuator response. Application.getResultantTuples sets ACTUATOR
        // direction for these edges; the provider routes it down through the access fog node.
        app.addAppEdge(MOD_A, ACT_A,
                1.0, s.responseNetUnits, OUT_A, Tuple.DOWN, AppEdge.ACTUATOR);
        app.addAppEdge(MOD_B, ACT_B,
                1.0, s.responseNetUnits, OUT_B, Tuple.DOWN, AppEdge.ACTUATOR);

        app.addTupleMapping(MOD_A, SEN_A, OUT_A, new FractionalSelectivity(1.0));
        app.addTupleMapping(MOD_B, SEN_B, OUT_B, new FractionalSelectivity(1.0));

        AppLoop loopA = new AppLoop(new ArrayList<String>() {{
            add(SEN_A); add(MOD_A); add(ACT_A);
        }});
        AppLoop loopB = new AppLoop(new ArrayList<String>() {{
            add(SEN_B); add(MOD_B); add(ACT_B);
        }});
        app.setLoops(Arrays.asList(loopA, loopB));
        return app;
    }

    private static InstrumentedFcfsScheduler addFcfsModule(Application app, String moduleName,
            String label, int userId, double mips, int ram, long size,
            LatencyStats systemStats, LatencyStats queueStats, LatencyStats serviceStats) {
        long bw = 1000;
        Map<Pair<String, String>, SelectivityModel> selectivity =
                new HashMap<Pair<String, String>, SelectivityModel>();

        InstrumentedFcfsScheduler scheduler = new InstrumentedFcfsScheduler(
                label, systemStats, queueStats, serviceStats);
        AppModule module = new AppModule(
                FogUtils.generateEntityId(), moduleName, app.getAppId(), userId,
                mips, ram, bw, size, "Xen", scheduler, selectivity);
        app.getModules().add(module);
        return scheduler;
    }

    private static void writeResults(String out, Application app) throws IOException {
        double lambdaA = s.taskRate * s.DA;
        double lambdaB = s.taskRate * s.DB;
        double rhoA = lambdaA / s.muA;
        double rhoB = lambdaB / s.muB;

        double mm1A = 1.0 / (s.muA - lambdaA);
        double mm1B = 1.0 / (s.muB - lambdaB);
        double matchedA = matchedSystemTime(lambdaA, s.muA, s.arrivalMode, s.serviceMode);
        double matchedB = matchedSystemTime(lambdaB, s.muB, s.arrivalMode, s.serviceMode);
        String reference = referenceModel(s.arrivalMode, s.serviceMode);

        double fixedA = fixedPathLatency(spatial.avgDistA, s.sigmaA);
        double fixedB = fixedPathLatency(spatial.avgDistB, s.sigmaB);

        double analyticMM1TotalA = fixedA + mm1A;
        double analyticMM1TotalB = fixedB + mm1B;
        double analyticMatchedTotalA = fixedA + matchedA;
        double analyticMatchedTotalB = fixedB + matchedB;

        double simA = endToEndA.mean();
        double simB = endToEndB.mean();
        double wrapperProvA = providerSystemA.mean();
        double wrapperProvB = providerSystemB.mean();
        double provA = schedulerSystemA.mean();
        double provB = schedulerSystemB.mean();
        double queueA = schedulerQueueA.mean();
        double queueB = schedulerQueueB.mean();
        double actualServiceA = schedulerServiceA.mean();
        double actualServiceB = schedulerServiceB.mean();
        double serviceA = sampledServiceA.mean();
        double serviceB = sampledServiceB.mean();
        double iaA = sampledInterarrivalA.mean();
        double iaB = sampledInterarrivalB.mean();
        double lambdaSampleA = (Double.isFinite(iaA) && iaA > 0.0) ? 1.0 / iaA : Double.NaN;
        double lambdaSampleB = (Double.isFinite(iaB) && iaB > 0.0) ? 1.0 / iaB : Double.NaN;
        double muSampleA = (Double.isFinite(serviceA) && serviceA > 0.0) ? 1.0 / serviceA : Double.NaN;
        double muSampleB = (Double.isFinite(serviceB) && serviceB > 0.0) ? 1.0 / serviceB : Double.NaN;
        double rhoSampleA = (Double.isFinite(lambdaSampleA) && Double.isFinite(muSampleA)) ? lambdaSampleA / muSampleA : Double.NaN;
        double rhoSampleB = (Double.isFinite(lambdaSampleB) && Double.isFinite(muSampleB)) ? lambdaSampleB / muSampleB : Double.NaN;
        double empiricalMM1A = empiricalMm1(lambdaSampleA, muSampleA);
        double empiricalMM1B = empiricalMm1(lambdaSampleB, muSampleB);

        double measuredFixedA = simA - provA;
        double measuredFixedB = simB - provB;

        double totalApeA = ape(simA, analyticMatchedTotalA);
        double totalApeB = ape(simB, analyticMatchedTotalB);
        double providerApeA = ape(provA, matchedA);
        double providerApeB = ape(provB, matchedB);
        double serviceExecApeA = ape(actualServiceA, 1.0 / s.muA);
        double serviceExecApeB = ape(actualServiceB, 1.0 / s.muB);
        double fixedApeA = ape(measuredFixedA, fixedA);
        double fixedApeB = ape(measuredFixedB, fixedB);
        double analyticIngressA = s.accessLatencyS + s.tS * (1.0 - s.sigmaA) * spatial.avgDistA
                + s.tupleNetUnits / s.uplinkBw + s.fogLinkLatencyS;
        double analyticIngressB = s.accessLatencyS + s.tS * (1.0 - s.sigmaB) * spatial.avgDistB
                + s.tupleNetUnits / s.uplinkBw + s.fogLinkLatencyS;
        double analyticEgress = s.responseNetUnits / s.downlinkBw + s.fogLinkLatencyS + s.actuatorLatencyS;
        double ingressApeA = ape(ingressA.mean(), analyticIngressA);
        double ingressApeB = ape(ingressB.mean(), analyticIngressB);
        double egressApeA = ape(egressA.mean(), analyticEgress);
        double egressApeB = ape(egressB.mean(), analyticEgress);

        double profitA = (s.priceA - s.cA) * s.DA;
        double profitB = (s.priceB - s.cB) * s.DB;

        long completed = endToEndA.count() + endToEndB.count();
        double measurementDuration = Math.max(1e-9, s.simulationTimeS - s.warmupS);
        double networkBytes = completed * (s.tupleNetUnits + s.responseNetUnits);
        double measuredNetworkThroughput = networkBytes / measurementDuration;
        double theoreticalNetworkThroughput = (lambdaA + lambdaB) *
                (s.tupleNetUnits + s.responseNetUnits);
        double networkApe = ape(measuredNetworkThroughput, theoreticalNetworkThroughput);

        boolean stochastic = "poisson".equalsIgnoreCase(s.arrivalMode)
                && "exponential".equalsIgnoreCase(s.serviceMode);
        boolean traceDriven = "trace".equalsIgnoreCase(s.arrivalMode);
        boolean ciA = !stochastic || contains(endToEndA.ciLow95(), endToEndA.ciHigh95(), analyticMatchedTotalA);
        boolean ciB = !stochastic || contains(endToEndB.ciLow95(), endToEndB.ciHigh95(), analyticMatchedTotalB);

        double threshold = stochastic ? s.acceptanceApePct : Math.min(2.0, s.acceptanceApePct);
        double cvTolerance = stochastic ? 0.15 : 0.02;
        boolean arrivalShapeOk = shapeWithin(sampledInterarrivalA.cv(), stochastic ? 1.0 : 0.0, cvTolerance)
                && shapeWithin(sampledInterarrivalB.cv(), stochastic ? 1.0 : 0.0, cvTolerance);
        boolean serviceShapeOk = shapeWithin(sampledServiceA.cv(), stochastic ? 1.0 : 0.0, cvTolerance)
                && shapeWithin(sampledServiceB.cv(), stochastic ? 1.0 : 0.0, cvTolerance);
        boolean pass = !traceDriven
                && totalApeA <= threshold && totalApeB <= threshold
                && providerApeA <= threshold && providerApeB <= threshold
                && serviceExecApeA <= threshold && serviceExecApeB <= threshold
                && fixedApeA <= Math.max(2.0, threshold) && fixedApeB <= Math.max(2.0, threshold)
                && ingressApeA <= Math.max(2.0, threshold) && ingressApeB <= Math.max(2.0, threshold)
                && egressApeA <= Math.max(2.0, threshold) && egressApeB <= Math.max(2.0, threshold)
                && networkApe <= Math.max(5.0, threshold)
                && arrivalShapeOk && serviceShapeOk;

        double standardA = timeKeeperAverage(app, 0);
        double standardB = timeKeeperAverage(app, 1);
        double nativeCpuA = timeKeeperTupleCpu(SEN_A);
        double nativeCpuB = timeKeeperTupleCpu(SEN_B);

        File file = new File(out);
        boolean header = !file.exists() || file.length() == 0;
        try (BufferedWriter w = new BufferedWriter(new FileWriter(file, true))) {
            if (header) {
                w.write("family,scenario,arrival_mode,service_mode,reference_model,replicate,seed,density_mode," +
                        "pA,pB,DA,DB,densityShareA,densityShareB,avgDistA,avgDistB,profitA,profitB," +
                        "lambdaA,lambdaB,muA,muB,rhoA,rhoB," +
                        "analyticMM1SystemA_s,analyticMM1SystemB_s,analyticMatchedSystemA_s,analyticMatchedSystemB_s," +
                        "analyticFixedA_s,analyticFixedB_s,analyticMM1TotalA_s,analyticMM1TotalB_s," +
                        "analyticMatchedTotalA_s,analyticMatchedTotalB_s," +
                        "simMeanA_s,simMeanB_s,simSdA_s,simSdB_s,simP95A_s,simP95B_s," +
                        "simCI95LowA_s,simCI95HighA_s,simCI95LowB_s,simCI95HighB_s,nA,nB," +
                        "providerSystemA_s,providerSystemB_s,providerQueueA_s,providerQueueB_s," +
                        "actualServiceA_s,actualServiceB_s,wrapperProviderSystemA_s,wrapperProviderSystemB_s,maxQueueA,maxQueueB," +
                        "sampleMeanServiceA_s,sampleMeanServiceB_s,sampleServiceCVA,sampleServiceCVB," +
                        "sampleMeanInterarrivalA_s,sampleMeanInterarrivalB_s,sampleInterarrivalCVA,sampleInterarrivalCVB," +
                        "sampleLambdaA,sampleLambdaB,sampleMuA,sampleMuB,sampleRhoA,sampleRhoB,empiricalMM1SystemA_s,empiricalMM1SystemB_s," +
                        "analyticIngressA_s,analyticIngressB_s,measuredIngressA_s,measuredIngressB_s," +
                        "analyticEgress_s,measuredEgressA_s,measuredEgressB_s,measuredFixedA_s,measuredFixedB_s," +
                        "timeKeeperAllA_s,timeKeeperAllB_s,timeKeeperCpuA_s,timeKeeperCpuB_s,totalAbsPctErrorA,totalAbsPctErrorB," +
                        "providerAbsPctErrorA,providerAbsPctErrorB,serviceExecAbsPctErrorA,serviceExecAbsPctErrorB,fixedAbsPctErrorA,fixedAbsPctErrorB," +
                        "ingressAbsPctErrorA,ingressAbsPctErrorB,egressAbsPctErrorA,egressAbsPctErrorB," +
                        "energyA_measurement_J,energyB_measurement_J,ifogsimNetworkUsageRaw,networkBytesMeasurement," +
                        "networkThroughputMeasured,networkThroughputTheory,networkAbsPctError," +
                        "slaThreshold_s,slaViolationRateA,slaViolationRateB,analyticInsideCI95A,analyticInsideCI95B," +
                        "arrivalShapeOk,serviceShapeOk,eventEpsilon_s,hostVmScheduler,cloudletScheduler,validationPass\n");
            }

            String[] row = new String[] {
                    s.family, s.scenario, s.arrivalMode, s.serviceMode, reference,
                    Integer.toString(s.replicate), Integer.toString(s.seed), s.densityMode,
                    fmt(s.priceA), fmt(s.priceB), fmt(s.DA), fmt(s.DB), fmt(spatial.shareA), fmt(spatial.shareB),
                    fmt(spatial.avgDistA), fmt(spatial.avgDistB), fmt(profitA), fmt(profitB),
                    fmt(lambdaA), fmt(lambdaB), fmt(s.muA), fmt(s.muB), fmt(rhoA), fmt(rhoB),
                    fmt(mm1A), fmt(mm1B), fmt(matchedA), fmt(matchedB), fmt(fixedA), fmt(fixedB),
                    fmt(analyticMM1TotalA), fmt(analyticMM1TotalB), fmt(analyticMatchedTotalA), fmt(analyticMatchedTotalB),
                    fmt(simA), fmt(simB), fmt(endToEndA.sd()), fmt(endToEndB.sd()), fmt(endToEndA.p95()), fmt(endToEndB.p95()),
                    fmt(endToEndA.ciLow95()), fmt(endToEndA.ciHigh95()), fmt(endToEndB.ciLow95()), fmt(endToEndB.ciHigh95()),
                    Integer.toString(endToEndA.count()), Integer.toString(endToEndB.count()),
                    fmt(provA), fmt(provB), fmt(queueA), fmt(queueB),
                    fmt(actualServiceA), fmt(actualServiceB), fmt(wrapperProvA), fmt(wrapperProvB),
                    Integer.toString(fcfsA == null ? 0 : fcfsA.maxQueue()), Integer.toString(fcfsB == null ? 0 : fcfsB.maxQueue()),
                    fmt(serviceA), fmt(serviceB), fmt(sampledServiceA.cv()), fmt(sampledServiceB.cv()),
                    fmt(iaA), fmt(iaB), fmt(sampledInterarrivalA.cv()), fmt(sampledInterarrivalB.cv()),
                    fmt(lambdaSampleA), fmt(lambdaSampleB), fmt(muSampleA), fmt(muSampleB), fmt(rhoSampleA), fmt(rhoSampleB),
                    fmt(empiricalMM1A), fmt(empiricalMM1B),
                    fmt(analyticIngressA), fmt(analyticIngressB), fmt(ingressA.mean()), fmt(ingressB.mean()),
                    fmt(analyticEgress), fmt(egressA.mean()), fmt(egressB.mean()), fmt(measuredFixedA), fmt(measuredFixedB),
                    fmt(standardA), fmt(standardB), fmt(nativeCpuA), fmt(nativeCpuB),
                    fmt(totalApeA), fmt(totalApeB), fmt(providerApeA), fmt(providerApeB),
                    fmt(serviceExecApeA), fmt(serviceExecApeB), fmt(fixedApeA), fmt(fixedApeB),
                    fmt(ingressApeA), fmt(ingressApeB), fmt(egressApeA), fmt(egressApeB),
                    fmt(Math.max(0.0, finalEnergyA - warmupEnergyA)), fmt(Math.max(0.0, finalEnergyB - warmupEnergyB)),
                    fmt(NetworkUsageMonitor.getNetworkUsage()), fmt(networkBytes), fmt(measuredNetworkThroughput),
                    fmt(theoreticalNetworkThroughput), fmt(networkApe), fmt(s.slaLatencyS),
                    fmt(endToEndA.slaViolationRate(s.slaLatencyS)), fmt(endToEndB.slaViolationRate(s.slaLatencyS)),
                    Boolean.toString(ciA), Boolean.toString(ciB), Boolean.toString(arrivalShapeOk),
                    Boolean.toString(serviceShapeOk), fmt(EVENT_EPSILON_S), "StreamOperatorScheduler",
                    "CloudletSchedulerSpaceShared", Boolean.toString(pass)
            };
            w.write(String.join(",", row));
            w.newLine();
            }

        System.out.printf(Locale.US,
                "VALIDATION %s | A analytic=%.6f sim=%.6f APE=%.3f%% | B analytic=%.6f sim=%.6f APE=%.3f%% | pass=%s%n",
                s.scenario, analyticMatchedTotalA, simA, totalApeA,
                analyticMatchedTotalB, simB, totalApeB, Boolean.toString(pass));
    }

    private static String fmt(double x) {
        return String.format(Locale.US, "%.9f", x);
    }

    private static double empiricalMm1(double lambda, double mu) {
        if (!Double.isFinite(lambda) || !Double.isFinite(mu) || lambda < 0.0 || mu <= lambda) return Double.NaN;
        return 1.0 / (mu - lambda);
    }

    private static boolean shapeWithin(double observedCv, double targetCv, double tolerance) {
        return Double.isFinite(observedCv) && Math.abs(observedCv - targetCv) <= tolerance;
    }

    private static double fixedPathLatency(double avgDistance, double sigma) {
        double spatialLatency = s.accessLatencyS + s.tS * (1.0 - sigma) * avgDistance;
        double up = s.tupleNetUnits / s.uplinkBw + s.fogLinkLatencyS;
        double down = s.responseNetUnits / s.downlinkBw + s.fogLinkLatencyS;
        return spatialLatency + up + down + s.actuatorLatencyS;
    }

    private static double ape(double measured, double reference) {
        if (!Double.isFinite(measured) || !Double.isFinite(reference) || reference == 0.0) return Double.NaN;
        return 100.0 * Math.abs(measured - reference) / Math.abs(reference);
    }

    private static boolean contains(double low, double high, double x) {
        return Double.isFinite(low) && Double.isFinite(high) && x >= low && x <= high;
    }

    private static double timeKeeperAverage(Application app, int index) {
        if (index >= app.getLoops().size()) return Double.NaN;
        Integer id = app.getLoops().get(index).getLoopId();
        Double v = TimeKeeper.getInstance().getLoopIdToCurrentAverage().get(id);
        return v == null ? Double.NaN : v;
    }

    private static double timeKeeperTupleCpu(String tupleType) {
        Double v = TimeKeeper.getInstance().getTupleTypeToAverageCpuTime().get(tupleType);
        return v == null ? Double.NaN : v;
    }

    private static String referenceModel(String arrival, String service) {
        if ("poisson".equalsIgnoreCase(arrival) && "exponential".equalsIgnoreCase(service)) return "M/M/1";
        if ("poisson".equalsIgnoreCase(arrival) && "fixed".equalsIgnoreCase(service)) return "M/D/1";
        if ("deterministic".equalsIgnoreCase(arrival) && "fixed".equalsIgnoreCase(service)) return "D/D/1";
        return "queue-reference-not-closed-form";
    }

    private static double matchedSystemTime(double lambda, double mu, String arrival, String service) {
        if (lambda <= 0.0) return 1.0 / mu;
        if (lambda >= mu) return Double.POSITIVE_INFINITY;

        if ("poisson".equalsIgnoreCase(arrival) && "exponential".equalsIgnoreCase(service)) {
            return 1.0 / (mu - lambda);
        }
        if ("poisson".equalsIgnoreCase(arrival) && "fixed".equalsIgnoreCase(service)) {
            double rho = lambda / mu;
            return 1.0 / mu + lambda / (2.0 * mu * mu * (1.0 - rho));
        }
        if ("deterministic".equalsIgnoreCase(arrival) && "fixed".equalsIgnoreCase(service)) {
            return 1.0 / mu;
        }
        if ("trace".equalsIgnoreCase(arrival)) return Double.NaN;
        return 1.0 / (mu - lambda);
    }

    private static SpatialStats computeSpatialStats(double xStar, String densityMode, int samples) {
        int n = Math.max(10000, samples);
        long countA = 0;
        double sumA = 0.0;
        double sumB = 0.0;
        for (int i = 0; i < n; i++) {
            double u = (i + 0.5) / n;
            double x = spatialQuantile(u, densityMode);
            if (x <= xStar) {
                countA++;
                sumA += x;
            } else {
                sumB += (1.0 - x);
            }
        }
        long countB = n - countA;
        double shareA = ((double)countA) / n;
        double shareB = 1.0 - shareA;
        double avgA = countA > 0 ? sumA / countA : 0.0;
        double avgB = countB > 0 ? sumB / countB : 0.0;
        return new SpatialStats(shareA, shareB, avgA, avgB);
    }

    private static double spatialQuantile(double u, String mode) {
        if ("uniform".equalsIgnoreCase(mode)) return u;
        if ("left".equalsIgnoreCase(mode)) return u * u;
        if ("right".equalsIgnoreCase(mode)) return 1.0 - (1.0 - u) * (1.0 - u);
        if ("center".equalsIgnoreCase(mode)) return 0.5 + 0.5 * Math.pow(2.0 * u - 1.0, 3.0);
        return u;
    }

    private static final class SpatialStats {
        final double shareA, shareB, avgDistA, avgDistB;
        SpatialStats(double shareA, double shareB, double avgDistA, double avgDistB) {
            this.shareA = shareA;
            this.shareB = shareB;
            this.avgDistA = avgDistA;
            this.avgDistB = avgDistB;
        }
    }

    private static final class AggregateValidationSensor extends Sensor {
        private final String arrivalMode;
        private final double meanCpuMI;
        private final String serviceMode;
        private final Random serviceRandom;
        private final double providerMips;
        private final LatencyStats serviceSamples;
        private final LatencyStats interarrivalSamples;
        private double lastEmission = Double.NaN;

        AggregateValidationSensor(String name, String tupleType, int userId, String appId,
                Distribution arrival, String arrivalMode, double meanCpuMI,
                String serviceMode, long serviceSeed, double providerMips,
                LatencyStats serviceSamples, LatencyStats interarrivalSamples) {
            super(name, tupleType, userId, appId, arrival);
            this.arrivalMode = arrivalMode;
            this.meanCpuMI = meanCpuMI;
            this.serviceMode = serviceMode;
            this.serviceRandom = new Random(serviceSeed);
            this.providerMips = providerMips;
            this.serviceSamples = serviceSamples;
            this.interarrivalSamples = interarrivalSamples;
        }

        @Override
        public void startEntity() {
            send(getGatewayDeviceId(), CloudSim.getMinTimeBetweenEvents(), FogEvents.SENSOR_JOINED, getGeoLocation());
            double first = "deterministic".equalsIgnoreCase(arrivalMode)
                    ? 0.5 * getTransmitDistribution().getMeanInterTransmitTime()
                    : getTransmitDistribution().getNextValue();
            first = Math.max(CloudSim.getMinTimeBetweenEvents(), first);
            send(getId(), first, FogEvents.EMIT_TUPLE);
        }

        @Override
        public void transmit() {
            AppEdge edge = null;
            for (AppEdge e : getApp().getEdges()) {
                if (e.getSource().equals(getTupleType())) {
                    edge = e;
                    break;
                }
            }
            if (edge == null) return;

            long cpuLength;
            if ("exponential".equalsIgnoreCase(serviceMode)) {
                double u = Math.max(1e-12, serviceRandom.nextDouble());
                cpuLength = Math.max(1L, Math.round(-meanCpuMI * Math.log(1.0 - u)));
            } else {
                cpuLength = Math.max(1L, Math.round(meanCpuMI));
            }

            long nwLength = Math.max(1L, Math.round(edge.getTupleNwLength()));
            Tuple tuple = new Tuple(
                    getAppId(), FogUtils.generateTupleId(), Tuple.UP,
                    cpuLength, 1, nwLength, 3,
                    new UtilizationModelFull(), new UtilizationModelFull(), new UtilizationModelFull());
            tuple.setUserId(getUserId());
            tuple.setTupleType(getTupleType());
            tuple.setDestModuleName(edge.getDestination());
            tuple.setSrcModuleName(getSensorName());

            int actualTupleId = updateTimings(getSensorName(), tuple.getDestModuleName());
            tuple.setActualTupleId(actualTupleId);

            double now = CloudSim.clock();
            if (now >= s.warmupS) {
                double serviceSeconds = cpuLength / providerMips;
                serviceSamples.add(serviceSeconds);
                serviceDemandByTuple.put(actualTupleId, serviceSeconds);
                if (Double.isFinite(lastEmission) && lastEmission >= s.warmupS) {
                    interarrivalSamples.add(now - lastEmission);
                }
            }
            lastEmission = now;

            send(getGatewayDeviceId(), getLatency(), FogEvents.TUPLE_ARRIVAL, tuple);
        }
    }

    /**
     * FCFS single-server scheduler instrumented independently from FogDevice/TimeKeeper.
     * This preserves iFogSim2's VM execution semantics while exposing native queue,
     * service and system times. The host-level VM scheduler is deliberately not
     * space-shared because FogDevice.updateAllocatedMips() repeatedly calls
     * deallocatePesForAllVms(), which is incompatible with v2.0.0 VmSchedulerSpaceShared.
     */
    private static final class InstrumentedFcfsScheduler extends CloudletSchedulerSpaceShared {
        private final String label;
        private final LatencyStats systemStats;
        private final LatencyStats queueStats;
        private final LatencyStats serviceStats;
        private final Map<Integer, Double> submitTimes = new HashMap<Integer, Double>();
        private final Map<Integer, Double> startTimes = new HashMap<Integer, Double>();
        private int maxQueue = 0;

        InstrumentedFcfsScheduler(String label, LatencyStats systemStats,
                LatencyStats queueStats, LatencyStats serviceStats) {
            super();
            this.label = label;
            this.systemStats = systemStats;
            this.queueStats = queueStats;
            this.serviceStats = serviceStats;
        }

        private int actualId(Cloudlet cl) {
            if (cl instanceof Tuple) return ((Tuple)cl).getActualTupleId();
            return cl.getCloudletId();
        }

        private boolean postWarmup(Cloudlet cl) {
            if (!(cl instanceof Tuple)) return CloudSim.clock() >= s.warmupS;
            Double emit = TimeKeeper.getInstance().getEmitTimes().get(((Tuple)cl).getActualTupleId());
            return emit != null && emit >= s.warmupS;
        }

        @Override
        public double cloudletSubmit(Cloudlet cloudlet, double fileTransferTime) {
            int id = actualId(cloudlet);
            submitTimes.put(id, CloudSim.clock());
            double estimate = super.cloudletSubmit(cloudlet, fileTransferTime);
            if (estimate > 0.0 && !startTimes.containsKey(id)) {
                startTimes.put(id, CloudSim.clock());
            }
            maxQueue = Math.max(maxQueue, getCloudletWaitingList().size());
            return estimate;
        }

        @Override
        public double updateVmProcessing(double currentTime, List<Double> mipsShare) {
            double next = super.updateVmProcessing(currentTime, mipsShare);
            // A waiting cloudlet promoted by super.updateVmProcessing starts exactly now.
            for (ResCloudlet rcl : this.<ResCloudlet>getCloudletExecList()) {
                int id = actualId(rcl.getCloudlet());
                if (!startTimes.containsKey(id)) startTimes.put(id, currentTime);
            }
            maxQueue = Math.max(maxQueue, getCloudletWaitingList().size());
            return next;
        }

        @Override
        public void cloudletFinish(ResCloudlet rcl) {
            Cloudlet cl = rcl.getCloudlet();
            int id = actualId(cl);
            Double submit = submitTimes.get(id);
            Double start = startTimes.get(id);
            if (submit != null && start != null && postWarmup(cl)) {
                queueStats.add(Math.max(0.0, start - submit));
                serviceStats.add(Math.max(0.0, CloudSim.clock() - start));
                systemStats.add(Math.max(0.0, CloudSim.clock() - submit));
            }
            super.cloudletFinish(rcl);
            submitTimes.remove(id);
            startTimes.remove(id);
        }

        int maxQueue() { return maxQueue; }

        @Override
        public String toString() { return "InstrumentedFcfsScheduler(" + label + ")"; }
    }

    private static final class InstrumentedFogDevice extends FogDevice {
        private final String providerLabel;
        private final String moduleName;
        private final String actuatorType;
        private final LatencyStats systemStats;
        private final LatencyStats queueStats;
        private final LatencyStats ingressStats;
        private final Map<Integer, Double> providerArrival = new HashMap<Integer, Double>();

        InstrumentedFogDevice(String name, String providerLabel,
                String moduleName, String actuatorType,
                FogDeviceCharacteristics characteristics,
                AppModuleAllocationPolicy allocationPolicy,
                List<Storage> storageList, double schedulingInterval,
                double uplinkBandwidth, double downlinkBandwidth,
                double uplinkLatency, double ratePerMips,
                LatencyStats systemStats, LatencyStats queueStats, LatencyStats ingressStats) throws Exception {
            super(name, characteristics, allocationPolicy, storageList, schedulingInterval,
                    uplinkBandwidth, downlinkBandwidth, uplinkLatency, ratePerMips);
            this.providerLabel = providerLabel;
            this.moduleName = moduleName;
            this.actuatorType = actuatorType;
            this.systemStats = systemStats;
            this.queueStats = queueStats;
            this.ingressStats = ingressStats;
        }

        /**
         * PowerDatacenter in the stock iFogSim2 fork schedules processing updates at a fixed
         * scheduling interval, even when the CloudletScheduler reports the exact next completion
         * time. That behavior is appropriate for coarse power-management experiments but biases
         * sub-second queueing validation. Here the next VM_DATACENTER_EVENT is scheduled at the
         * exact completion time returned by the Cloudlet scheduler.
         */
        @Override
        protected void updateCloudletProcessing() {
            double currentTime = CloudSim.clock();
            if (currentTime <= getLastProcessTime()) return;

            double nextEvent = updateCloudetProcessingWithoutSchedulingFutureEventsForce();
            CloudSim.cancelAll(getId(), new PredicateType(CloudSimTags.VM_DATACENTER_EVENT));

            if (Double.isFinite(nextEvent) && nextEvent != Double.MAX_VALUE && nextEvent > currentTime) {
                double delay = Math.max(CloudSim.getMinTimeBetweenEvents(), nextEvent - currentTime);
                send(getId(), delay, CloudSimTags.VM_DATACENTER_EVENT);
            }
        }

        @Override
        protected void processTupleArrival(SimEvent ev) {
            Tuple tuple = (Tuple)ev.getData();
            if (moduleName.equals(tuple.getDestModuleName())) {
                Double emit = TimeKeeper.getInstance().getEmitTimes().get(tuple.getActualTupleId());
                if (emit != null && emit >= s.warmupS) {
                    providerArrival.put(tuple.getActualTupleId(), CloudSim.clock());
                    ingressStats.add(CloudSim.clock() - emit);
                }
            }
            super.processTupleArrival(ev);
        }

        @Override
        protected void sendTupleToActuator(Tuple tuple) {
            if (actuatorType.equals(tuple.getDestModuleName())) {
                Double arrival = providerArrival.remove(tuple.getActualTupleId());
                if (arrival != null) {
                    double sojourn = CloudSim.clock() - arrival;
                    systemStats.add(sojourn);
                    Double service = serviceDemandByTuple.remove(tuple.getActualTupleId());
                    if (service != null) queueStats.add(Math.max(0.0, sojourn - service));
                    providerDepartureByTuple.put(tuple.getActualTupleId(), CloudSim.clock());
                }
            }
            super.sendTupleToActuator(tuple);
        }

        @Override
        public String toString() {
            return "InstrumentedFogDevice(" + providerLabel + ")";
        }
    }

    private static final class MeasuringActuator extends Actuator {
        private final LatencyStats stats;
        private final LatencyStats egressStats;
        private final double warmup;

        MeasuringActuator(String name, int userId, String appId,
                String actuatorType, LatencyStats stats, LatencyStats egressStats, double warmup) {
            super(name, userId, appId, actuatorType);
            this.stats = stats;
            this.egressStats = egressStats;
            this.warmup = warmup;
        }

        @Override
        public void processEvent(SimEvent ev) {
            if (ev.getTag() == FogEvents.TUPLE_ARRIVAL) {
                Tuple tuple = (Tuple)ev.getData();
                Double start = TimeKeeper.getInstance().getEmitTimes().get(tuple.getActualTupleId());
                if (start != null && start >= warmup) {
                    stats.add(CloudSim.clock() - start);
                    Double departure = providerDepartureByTuple.remove(tuple.getActualTupleId());
                    if (departure != null) egressStats.add(CloudSim.clock() - departure);
                }
            }
            super.processEvent(ev);
        }
    }

    private static final class ValidationController extends Controller {
        private static final int WARMUP_EVENT = 987654;

        ValidationController(String name, List<FogDevice> fogDevices,
                List<Sensor> sensors, List<Actuator> actuators) {
            super(name, fogDevices, sensors, actuators);
        }

        @Override
        public void startEntity() {
            super.startEntity();
            send(getId(), s.warmupS, WARMUP_EVENT);
        }

        @Override
        public void processEvent(SimEvent ev) {
            if (ev.getTag() == WARMUP_EVENT) {
                warmupEnergyA = fogA.getEnergyConsumption();
                warmupEnergyB = fogB.getEnergyConsumption();
                return;
            }
            if (ev.getTag() == FogEvents.STOP_SIMULATION) {
                finalEnergyA = fogA.getEnergyConsumption();
                finalEnergyB = fogB.getEnergyConsumption();
                // In this CloudSim fork stopSimulation() only changes a flag and may not terminate
                // an active event queue. terminateSimulation() is required to stop at the intended T.
                CloudSim.terminateSimulation();
                return;
            }
            super.processEvent(ev);
        }
    }

    private static final class LatencyStats {
        private final List<Double> values = new ArrayList<Double>();

        void add(double x) {
            if (Double.isFinite(x) && x >= 0.0) values.add(x);
        }
        int count() { return values.size(); }
        double mean() {
            if (values.isEmpty()) return Double.NaN;
            double z = 0.0;
            for (double x : values) z += x;
            return z / values.size();
        }
        double sd() {
            if (values.size() < 2) return Double.NaN;
            double m = mean();
            double z = 0.0;
            for (double x : values) z += (x - m) * (x - m);
            return Math.sqrt(z / (values.size() - 1));
        }        double cv() {
            double m = mean();
            double sdev = sd();
            return (!Double.isFinite(m) || m == 0.0 || !Double.isFinite(sdev)) ? Double.NaN : sdev / m;
        }
        double p95() {
            if (values.isEmpty()) return Double.NaN;
            List<Double> c = new ArrayList<Double>(values);
            Collections.sort(c);
            int idx = (int)Math.ceil(0.95 * c.size()) - 1;
            idx = Math.max(0, Math.min(c.size() - 1, idx));
            return c.get(idx);
        }
        double ciLow95() {
            if (values.size() < 2) return Double.NaN;
            return mean() - 1.96 * sd() / Math.sqrt(values.size());
        }
        double ciHigh95() {
            if (values.size() < 2) return Double.NaN;
            return mean() + 1.96 * sd() / Math.sqrt(values.size());
        }
        double slaViolationRate(double threshold) {
            if (values.isEmpty()) return Double.NaN;
            int n = 0;
            for (double x : values) if (x > threshold) n++;
            return ((double)n) / values.size();
        }
    }

    private static final class ExponentialInterarrival extends Distribution {
        private final double mean;
        ExponentialInterarrival(double mean, long seed) {
            this.mean = mean;
            this.random = new Random(seed);
        }
        public double getNextValue() {
            double u = Math.max(1e-12, random.nextDouble());
            return -mean * Math.log(1.0 - u);
        }
        public int getDistributionType() { return 4; }
        public double getMeanInterTransmitTime() { return mean; }
    }

    private static final class TraceInterarrival extends Distribution {
        private final List<Double> values = new ArrayList<Double>();
        private int idx;
        private final double scale;
        private final double mean;

        TraceInterarrival(String file, double mean, double scale, long seed) throws IOException {
            if (file == null || file.isEmpty()) throw new IOException("Trace mode requires trace_file");
            this.scale = scale;
            this.mean = mean;
            this.random = new Random(seed);
            try (BufferedReader br = new BufferedReader(new FileReader(file))) {
                String line;
                while ((line = br.readLine()) != null) {
                    line = line.trim();
                    if (line.isEmpty() || line.startsWith("#")) continue;
                    String token = line.split(",")[0].trim();
                    try {
                        double x = Double.parseDouble(token);
                        if (x > 0) values.add(x);
                    } catch (NumberFormatException ignored) {}
                }
            }
            if (values.isEmpty()) throw new IOException("No positive inter-arrival values in " + file);
            idx = (int)(Math.abs(seed) % values.size());
        }

        public double getNextValue() {
            double x = values.get(idx);
            idx = (idx + 1) % values.size();
            return x * mean * scale;
        }
        public int getDistributionType() { return 5; }
        public double getMeanInterTransmitTime() {
            double z = 0.0;
            for (double x : values) z += x;
            return mean * scale * z / values.size();
        }
    }

    private static Scenario readScenario(String path, int rowWanted) throws IOException {
        try (BufferedReader br = new BufferedReader(new FileReader(path))) {
            String h = br.readLine();
            if (h == null) throw new IOException("Empty CSV");
            String[] headers = h.split(",", -1);
            String line;
            int row = 0;
            while ((line = br.readLine()) != null) {
                if (line.trim().isEmpty() || line.startsWith("#")) continue;
                row++;
                if (row != rowWanted) continue;
                String[] v = line.split(",", -1);
                if (v.length != headers.length) throw new IOException("Column mismatch row " + row);
                Map<String, String> m = new LinkedHashMap<String, String>();
                for (int i = 0; i < headers.length; i++) m.put(headers[i].trim(), v[i].trim());
                return Scenario.from(m);
            }
        }
        throw new IOException("Scenario row not found: " + rowWanted);
    }

    private static final class Scenario {
        String family, scenario, arrivalMode, serviceMode, densityMode, traceFile;
        int replicate, seed, totalUsers, fogRamMB, moduleSize, spatialSamples;
        boolean quiet;
        double V, c, cA, cB, tS, sigma, sigmaA, sigmaB, taskRate, muA, muB,
                omegaL, priceA, priceB, xStar, DA, DB, tupleCpuMI, tupleNetUnits,
                responseCpuMI, responseNetUnits, accessLatencyS, actuatorLatencyS,
                slaLatencyS, ratePerMips, busyPowerW, idlePowerW,
                simulationTimeS, warmupS, traceScale, fogLinkLatencyS, acceptanceApePct;
        long uplinkBw, downlinkBw;

        static Scenario from(Map<String, String> m) {
            Scenario q = new Scenario();
            q.family = g(m, "family");
            q.scenario = g(m, "scenario");
            q.replicate = i(m, "replicate");
            q.arrivalMode = g(m, "arrival_mode");
            q.seed = i(m, "seed");
            q.densityMode = g(m, "density_mode");
            q.V = d(m, "V");
            q.c = d(m, "c");
            q.cA = optd(m, "cA", q.c);
            q.cB = optd(m, "cB", q.c);
            q.tS = d(m, "t_s");
            q.sigma = d(m, "sigma");
            q.sigmaA = optd(m, "sigmaA", q.sigma);
            q.sigmaB = optd(m, "sigmaB", q.sigma);
            q.taskRate = d(m, "r_tasks_s");
            q.muA = d(m, "muA_tasks_s");
            q.muB = d(m, "muB_tasks_s");
            q.omegaL = d(m, "omegaL");
            q.priceA = d(m, "pA");
            q.priceB = d(m, "pB");
            q.xStar = d(m, "x_star");
            q.DA = d(m, "DA");
            q.DB = d(m, "DB");
            q.totalUsers = i(m, "N_users");
            q.tupleCpuMI = d(m, "tuple_cpu_MI");
            q.tupleNetUnits = d(m, "tuple_net_units");
            q.responseCpuMI = d(m, "response_cpu_MI");
            q.responseNetUnits = d(m, "response_net_units");
            q.accessLatencyS = d(m, "access_latency_s");
            q.actuatorLatencyS = d(m, "actuator_latency_s");
            q.slaLatencyS = d(m, "sla_latency_s");
            q.fogRamMB = i(m, "fog_ram_mb");
            q.uplinkBw = l(m, "uplink_bw");
            q.downlinkBw = l(m, "downlink_bw");
            q.ratePerMips = d(m, "rate_per_mips");
            q.busyPowerW = d(m, "busy_power_W");
            q.idlePowerW = d(m, "idle_power_W");
            q.simulationTimeS = d(m, "simulation_time_s");
            q.traceFile = m.containsKey("trace_file") ? m.get("trace_file") : "";
            q.traceScale = optd(m, "trace_scale", 1.0);
            q.serviceMode = opt(m, "service_mode",
                    "poisson".equalsIgnoreCase(q.arrivalMode) ? "exponential" : "fixed");
            q.warmupS = optd(m, "warmup_s", Math.min(1000.0, 0.1 * q.simulationTimeS));
            q.fogLinkLatencyS = optd(m, "fog_link_latency_s", 0.001);
            q.moduleSize = opti(m, "module_size", 10000);
            q.spatialSamples = opti(m, "spatial_samples", 200000);
            q.acceptanceApePct = optd(m, "acceptance_ape_pct", 5.0);
            q.quiet = optb(m, "quiet", true);

            if (Math.abs(q.DA + q.DB - 1.0) > 1e-5)
                throw new IllegalArgumentException("Full-coverage rows require DA+DB=1");
            if (q.taskRate * q.DA >= q.muA || q.taskRate * q.DB >= q.muB)
                throw new IllegalArgumentException("Analytical queue unstable");
            if (q.warmupS >= q.simulationTimeS)
                throw new IllegalArgumentException("warmup_s must be smaller than simulation_time_s");
            if (q.muA <= 0 || q.muB <= 0 || q.tupleCpuMI <= 0)
                throw new IllegalArgumentException("mu and tuple_cpu_MI must be positive");
            return q;
        }

        static String g(Map<String, String> m, String k) {
            String v = m.get(k);
            if (v == null || v.isEmpty()) throw new IllegalArgumentException("Missing " + k);
            return v;
        }
        static String opt(Map<String, String> m, String k, String def) {
            String v = m.get(k);
            return (v == null || v.isEmpty()) ? def : v;
        }
        static double d(Map<String, String> m, String k) { return Double.parseDouble(g(m, k)); }
        static int i(Map<String, String> m, String k) { return Integer.parseInt(g(m, k)); }
        static long l(Map<String, String> m, String k) { return Long.parseLong(g(m, k)); }
        static double optd(Map<String, String> m, String k, double def) {
            String v = m.get(k);
            return (v == null || v.isEmpty()) ? def : Double.parseDouble(v);
        }
        static int opti(Map<String, String> m, String k, int def) {
            String v = m.get(k);
            return (v == null || v.isEmpty()) ? def : Integer.parseInt(v);
        }
        static boolean optb(Map<String, String> m, String k, boolean def) {
            String v = m.get(k);
            return (v == null || v.isEmpty()) ? def : Boolean.parseBoolean(v);
        }
    }
}