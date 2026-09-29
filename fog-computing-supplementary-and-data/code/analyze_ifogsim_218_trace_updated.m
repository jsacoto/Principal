function analyze_ifogsim_218_trace_updated(fullResultsFile, traceSummaryFile)
% ANALYZE_IFOGSIM_218_TRACE_UPDATED
% Re-analyzes the 218-row iFogSim2 output and incorporates the revised
% interarrival-trace validation summary as a separate arrival-validation gate.
%
% Usage:
%   analyze_ifogsim_218_trace_updated( ...
%       fullfile('data','ifogsim_v5_results_218_complete.csv'), ...
%       fullfile('data','replace_with_interarrival_trace_s_validation_summary.csv'));
%
% TikZ export:
%   Install matlab2tikz and add it to the MATLAB path. When matlab2tikz is
%   available, every MATLAB figure below is exported automatically to .tex.
%
% IMPORTANT:
%   The revised trace CSV contains input-trace validation diagnostics, not a
%   new Java/iFogSim2 latency simulation. Therefore the script reports both:
%   (1) the observed 218-row validationPass from iFogSim2, and
%   (2) a projected validation status obtained by replacing only the trace
%       arrival gate when the revised trace satisfies the explicit diagnostic.

if nargin < 1
    fullResultsFile = 'ifogsim_v5_results_218_complete(1).csv';
end
if nargin < 2
    traceSummaryFile = 'replace_with_interarrival_trace_s_validation_summary.csv';
end

T = readtable(fullResultsFile,'VariableNamingRule','preserve');
R = readtable(traceSummaryFile,'VariableNamingRule','preserve');

valid = localLogical(T.validationPass);
arrivalOk = localLogical(T.arrivalShapeOk);
serviceOk = localLogical(T.serviceShapeOk);

poisson = strcmpi(string(T.arrival_mode),'poisson') & strcmpi(string(T.service_mode),'exponential');
determ  = strcmpi(string(T.arrival_mode),'deterministic') & strcmpi(string(T.service_mode),'fixed');
traceIdx = strcmpi(string(T.arrival_mode),'trace');

A = R(strcmpi(string(R.scope),'provider_A_replay_window'),:);
B = R(strcmpi(string(R.scope),'provider_B_replay_window'),:);
G = R(strcmpi(string(R.scope),'global'),:);
if height(A)~=1 || height(B)~=1 || height(G)~=1
    error('Trace summary must contain global, provider_A_replay_window and provider_B_replay_window rows.');
end

tr = T(find(traceIdx,1,'first'),:);
oldLambdaErrA = abs(tr.sampleLambdaA-tr.lambdaA)/tr.lambdaA*100;
oldLambdaErrB = abs(tr.sampleLambdaB-tr.lambdaB)/tr.lambdaB*100;

% The component threshold below is reconstructed exactly from the supplied
% 218-row output: validationPass equals arrivalShapeOk AND serviceShapeOk AND
% every listed component error <= 5% for all 218 rows.
componentErrorCols = {'providerAbsPctErrorA','providerAbsPctErrorB', ...
    'serviceExecAbsPctErrorA','serviceExecAbsPctErrorB', ...
    'fixedAbsPctErrorA','fixedAbsPctErrorB', ...
    'ingressAbsPctErrorA','ingressAbsPctErrorB', ...
    'egressAbsPctErrorA','egressAbsPctErrorB','networkAbsPctError'};
reconstructed = arrivalOk & serviceOk;
for k=1:numel(componentErrorCols)
    x = T.(componentErrorCols{k});
    x(isnan(x)) = 0;
    reconstructed = reconstructed & x <= 5.0;
end
fprintf('\nGate reconstruction match: %d / %d rows\n',sum(reconstructed==valid),height(T));

% Explicit revised-trace diagnostic. This is kept visible rather than
% silently claiming it is hidden Java logic.
cvTol = 0.05;          % |CV - 1| <= 0.05
lambdaTolPct = 5.0;    % lambda APE <= 5%
traceInputPass = abs(A.cv-1)<=cvTol && abs(B.cv-1)<=cvTol && ...
    A.lambda_abs_pct_error<=lambdaTolPct && B.lambda_abs_pct_error<=lambdaTolPct;

oldTraceComponentsPass = serviceOk(traceIdx);
for k=1:numel(componentErrorCols)
    x = tr.(componentErrorCols{k});
    if ~isnan(x), oldTraceComponentsPass = oldTraceComponentsPass && x<=5.0; end
end
oldTraceOnlyArrivalBlocker = oldTraceComponentsPass && ~arrivalOk(traceIdx) && ~valid(traceIdx);

projectedValid = valid;
if traceInputPass && oldTraceOnlyArrivalBlocker
    projectedValid(traceIdx) = true;
end

fprintf('\n=== Updated iFogSim2 analysis with revised interarrival trace ===\n');
fprintf('Rows: %d\n',height(T));
fprintf('Observed PASS=%d | FAIL=%d | rate=%.3f%%\n',sum(valid),sum(~valid),100*mean(valid));
fprintf('Projected PASS=%d | FAIL=%d | rate=%.3f%%\n',sum(projectedValid),sum(~projectedValid),100*mean(projectedValid));
fprintf('\nRevised trace global: n=%d, mean multiplier=%.9f, CV=%.9f\n',G.n,G.mean_multiplier_or_ratio,G.cv);
fprintf('Provider A: n=%d, CV=%.9f, lambda APE=%.6f%%\n',A.n,A.cv,A.lambda_abs_pct_error);
fprintf('Provider B: n=%d, CV=%.9f, lambda APE=%.6f%%\n',B.n,B.cv,B.lambda_abs_pct_error);
fprintf('Old -> new lambda APE A: %.6f%% -> %.6f%%\n',oldLambdaErrA,A.lambda_abs_pct_error);
fprintf('Old -> new lambda APE B: %.6f%% -> %.6f%%\n',oldLambdaErrB,B.lambda_abs_pct_error);
fprintf('Old -> new interarrival CV A: %.6f -> %.6f\n',tr.sampleInterarrivalCVA,A.cv);
fprintf('Old -> new interarrival CV B: %.6f -> %.6f\n',tr.sampleInterarrivalCVB,B.cv);

if any(poisson)
    fprintf('\nMean Poisson/exponential total APE: A=%.3f%%, B=%.3f%%\n', ...
        mean(T.totalAbsPctErrorA(poisson),'omitnan'),mean(T.totalAbsPctErrorB(poisson),'omitnan'));
    fprintf('Mean Poisson interarrival CV: A=%.3f, B=%.3f\n', ...
        mean(T.sampleInterarrivalCVA(poisson),'omitnan'),mean(T.sampleInterarrivalCVB(poisson),'omitnan'));
end
if any(determ)
    fprintf('Mean deterministic total APE: A=%.3f%%, B=%.3f%%\n', ...
        mean(T.totalAbsPctErrorA(determ),'omitnan'),mean(T.totalAbsPctErrorB(determ),'omitnan'));
end

% Output comparison table.
C = table(["A";"B"], ...
    [tr.lambdaA;tr.lambdaB], ...
    [tr.sampleLambdaA;tr.sampleLambdaB], ...
    [A.sample_lambda;B.sample_lambda], ...
    [oldLambdaErrA;oldLambdaErrB], ...
    [A.lambda_abs_pct_error;B.lambda_abs_pct_error], ...
    [tr.sampleInterarrivalCVA;tr.sampleInterarrivalCVB], ...
    [A.cv;B.cv], ...
    'VariableNames',{'provider','nominal_lambda','old_sample_lambda','new_sample_lambda', ...
    'old_lambda_abs_pct_error','new_lambda_abs_pct_error','old_interarrival_cv','new_interarrival_cv'});
writetable(C,'trace_validation_old_vs_new_matlab.csv');

% Family summary, observed and projected.
families = unique(string(T.family),'stable');
S = table('Size',[numel(families),7], ...
    'VariableTypes',{'string','double','double','double','double','double','double'}, ...
    'VariableNames',{'family','n','observed_pass','observed_pass_rate_pct', ...
    'projected_pass','projected_pass_rate_pct','mean_network_ape_pct'});
for k=1:numel(families)
    idx = string(T.family)==families(k);
    S.family(k)=families(k);
    S.n(k)=sum(idx);
    S.observed_pass(k)=sum(valid(idx));
    S.observed_pass_rate_pct(k)=100*mean(valid(idx));
    S.projected_pass(k)=sum(projectedValid(idx));
    S.projected_pass_rate_pct(k)=100*mean(projectedValid(idx));
    S.mean_network_ape_pct(k)=mean(T.networkAbsPctError(idx),'omitnan');
end
writetable(S,'updated_summary_by_family_matlab.csv');

% Figure 1: analytical vs simulated latency.
xA=T.analyticMatchedTotalA_s; yA=T.simMeanA_s;
xB=T.analyticMatchedTotalB_s; yB=T.simMeanB_s;
maskA=isfinite(xA)&isfinite(yA); maskB=isfinite(xB)&isfinite(yB);
vals=[xA(maskA);yA(maskA);xB(maskB);yB(maskB)];
lo=min(vals); hi=max(vals);
figure('Color','w');
plot(xA(maskA),yA(maskA),'o','DisplayName','Provider A'); hold on;
plot(xB(maskB),yB(maskB),'s','DisplayName','Provider B');
plot([lo hi],[lo hi],'--','DisplayName','Identity');
xlabel('Analytical latency (s)'); ylabel('iFogSim2 latency (s)');
title('Strict validation: analytical vs iFogSim2 latency');
legend('Location','best'); grid on;
exportgraphics(gcf,'fig1_analytical_vs_simulated_updated_matlab.png','Resolution',300);
localTikzExport('fig1_analytical_vs_simulated_updated_matlab.tex');

% Figure 2: observed vs revised-trace projected pass rate.
figure('Color','w');
b=bar(categorical(S.family),[S.observed_pass_rate_pct S.projected_pass_rate_pct],'grouped'); %#ok<NASGU>
ylabel('Validation pass rate (%)'); xlabel('Scenario family');
title('Strict validation pass rate by family');
legend({'Observed iFogSim2 output','With revised trace arrival gate'},'Location','best');
grid on; ylim([0 105]);
exportgraphics(gcf,'fig2_pass_rate_observed_vs_trace_updated_matlab.png','Resolution',300);
localTikzExport('fig2_pass_rate_observed_vs_trace_updated_matlab.tex');

% Figure 3: lambda error old vs new.
figure('Color','w');
bar(categorical(C.provider),[C.old_lambda_abs_pct_error C.new_lambda_abs_pct_error],'grouped'); hold on;
yline(5,'--','5% strict component scale');
ylabel('Absolute lambda error (%)');
title('Interarrival-rate validation: previous vs revised trace');
legend({'Previous trace','Revised trace'},'Location','best'); grid on;
exportgraphics(gcf,'fig3_trace_lambda_error_old_vs_new_matlab.png','Resolution',300);
localTikzExport('fig3_trace_lambda_error_old_vs_new_matlab.tex');

% Figure 4: CV old vs new.
figure('Color','w');
bar(categorical(C.provider),[C.old_interarrival_cv C.new_interarrival_cv],'grouped'); hold on;
yline(1,'--','Exponential target CV=1');
ylabel('Interarrival coefficient of variation'); ylim([0.94 1.07]);
title('Interarrival-shape validation: previous vs revised trace');
legend({'Previous trace','Revised trace'},'Location','best'); grid on;
exportgraphics(gcf,'fig4_trace_cv_old_vs_new_matlab.png','Resolution',300);
localTikzExport('fig4_trace_cv_old_vs_new_matlab.tex');

fprintf('\nMATLAB outputs written. If matlab2tikz is on the path, TikZ .tex files were also exported.\n');
end

function x = localLogical(v)
if islogical(v)
    x=v;
else
    s=lower(string(v));
    x=(s=="true") | (s=="1");
end
end

function localTikzExport(filename)
if exist('matlab2tikz','file')==2
    matlab2tikz(filename,'showInfo',false);
else
    warning('matlab2tikz not found. PNG was created; add matlab2tikz to the MATLAB path for native TikZ export.');
end
end