import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Minimal dependency-free recorder for tuple-level end-to-end latency.
 * Integrate calls to record("A", latencySeconds, slaSeconds) and
 * record("B", latencySeconds, slaSeconds) when each measured tuple completes.
 */
public final class TailLatencyRecorder {
    private final Map<String, List<Double>> samples = new HashMap<>();
    private final Map<String, Integer> slaViolations = new HashMap<>();
    private final Map<String, Double> slaThresholds = new HashMap<>();

    public void record(String provider, double latencySeconds, double slaSeconds) {
        if (!Double.isFinite(latencySeconds) || latencySeconds < 0.0) {
            return;
        }
        samples.computeIfAbsent(provider, k -> new ArrayList<>()).add(latencySeconds);
        slaThresholds.put(provider, slaSeconds);
        if (latencySeconds > slaSeconds) {
            slaViolations.put(provider, slaViolations.getOrDefault(provider, 0) + 1);
        }
    }

    public int count(String provider) {
        return samples.getOrDefault(provider, Collections.emptyList()).size();
    }

    public double mean(String provider) {
        List<Double> x = samples.getOrDefault(provider, Collections.emptyList());
        if (x.isEmpty()) return Double.NaN;
        double sum = 0.0;
        for (double v : x) sum += v;
        return sum / x.size();
    }

    /** R-7 / NumPy-like linear interpolation quantile. */
    public double quantile(String provider, double p) {
        if (p < 0.0 || p > 1.0) throw new IllegalArgumentException("p must be in [0,1]");
        List<Double> raw = samples.getOrDefault(provider, Collections.emptyList());
        if (raw.isEmpty()) return Double.NaN;
        List<Double> x = new ArrayList<>(raw);
        Collections.sort(x);
        if (x.size() == 1) return x.get(0);
        double h = (x.size() - 1) * p;
        int lo = (int) Math.floor(h);
        int hi = (int) Math.ceil(h);
        if (lo == hi) return x.get(lo);
        double w = h - lo;
        return x.get(lo) * (1.0 - w) + x.get(hi) * w;
    }

    public double slaViolationRate(String provider) {
        int n = count(provider);
        if (n == 0) return Double.NaN;
        return ((double) slaViolations.getOrDefault(provider, 0)) / n;
    }

    public void writeSummaryCsv(String path) throws IOException {
        try (BufferedWriter w = new BufferedWriter(new FileWriter(path))) {
            w.write("provider,n,mean_s,p95_s,p99_s,sla_s,sla_violation_rate_pct\n");
            List<String> providers = new ArrayList<>(samples.keySet());
            Collections.sort(providers);
            for (String provider : providers) {
                w.write(String.format(Locale.US,
                    "%s,%d,%.12f,%.12f,%.12f,%.12f,%.9f%n",
                    provider,
                    count(provider),
                    mean(provider),
                    quantile(provider, 0.95),
                    quantile(provider, 0.99),
                    slaThresholds.getOrDefault(provider, Double.NaN),
                    100.0 * slaViolationRate(provider)));
            }
        }
    }

    public void writeRawCsv(String path) throws IOException {
        try (BufferedWriter w = new BufferedWriter(new FileWriter(path))) {
            w.write("provider,sample_index,latency_s\n");
            List<String> providers = new ArrayList<>(samples.keySet());
            Collections.sort(providers);
            for (String provider : providers) {
                List<Double> x = samples.get(provider);
                for (int i = 0; i < x.size(); i++) {
                    w.write(String.format(Locale.US, "%s,%d,%.12f%n", provider, i + 1, x.get(i)));
                }
            }
        }
    }
}
