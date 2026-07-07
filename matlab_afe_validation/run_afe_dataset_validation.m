%% ================================================================
%  Official AFE Input Dataset Batch Validation
%
%  Intended repo dataset layout:
%    afe_input_dataset/afe_input_NSR.csv
%    afe_input_dataset/afe_input_CHF.csv
%    afe_input_dataset/afe_input_ARR.csv
%    afe_input_dataset/afe_input_AFF.csv
%    afe_input_dataset/afe_input_record100_NSR.csv
%
%  Each CSV: sample_index, time_s, code_signed, voltage_V
%  Each PWL: time[s], voltage[V]
%
%  Run:
%    run_afe_dataset_validation
% ================================================================

clear; clc; close all;
rng(7);

results_dir = 'results_dataset';
if ~exist(results_dir, 'dir')
    mkdir(results_dir);
end

p = afe_adc_params();
filt = design_afe_filters(p);

% Save schematic-level parameter summary and common frequency response.
print_afe_spec_summary(p, results_dir);
plot_afe_frequency_response(p, filt, results_dir);

records = {'NSR', 'CHF', 'ARR', 'AFF', 'record100_NSR'};
prefer_format = 'csv';   % CSV is recommended for MATLAB analysis. Use 'pwl' to test PWL parsing.

all_metrics = table();
all_meta = table();

for i = 1:numel(records)
    rec = records{i};
    fprintf('\n===== Validating %s =====\n', rec);

    try
        [t, v_ecg_diff, src, meta] = load_afe_input_record(rec, p, prefer_format);
        fprintf('Input source: %s\n', src);

        [y, metrics] = afe_adc_model(t, v_ecg_diff, p, filt);

        % Add record information to summary tables.
        metrics.record_name = string(rec);
        metrics = movevars(metrics, 'record_name', 'Before', 1);
        meta.record_name = string(rec);

        rec_dir = fullfile(results_dir, rec);
        if ~exist(rec_dir, 'dir')
            mkdir(rec_dir);
        end

        plot_afe_time_domain(y, p, rec_dir);
        save_afe_outputs(y, metrics, rec_dir);

        all_metrics = [all_metrics; metrics]; %#ok<AGROW>
        all_meta = [all_meta; meta]; %#ok<AGROW>

        disp(metrics);
    catch ME
        warning('Skipping %s: %s', rec, ME.message);
    end
end

if ~isempty(all_metrics)
    writetable(all_metrics, fullfile(results_dir, 'afe_dataset_dynamic_range_summary.csv'));
end
if ~isempty(all_meta)
    writetable(all_meta, fullfile(results_dir, 'afe_dataset_input_summary.csv'));
end

fprintf('\nBatch validation finished. Results saved in ./%s/\n', results_dir);
