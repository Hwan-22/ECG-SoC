function [f, H] = freq_response_discrete(b, a, fs, nfft)
%FREQ_RESPONSE_DISCRETE  Toolbox-free discrete-time frequency response.

    if nargin < 4
        nfft = 8192;
    end

    f = linspace(0, fs/2, nfft).';
    z = exp(1j*2*pi*f/fs);

    % H(z) = (b0 + b1 z^-1 + ...)/(a0 + a1 z^-1 + ...)
    num = zeros(size(z));
    den = zeros(size(z));

    for k = 1:length(b)
        num = num + b(k) .* z.^(-(k-1));
    end
    for k = 1:length(a)
        den = den + a(k) .* z.^(-(k-1));
    end

    H = num ./ den;
end
