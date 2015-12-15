
fileID = fopen('test_log.txt','r');
textscan(fileID, '%s', 1, 'Delimiter', '\n');
data = textscan(fileID,'%d %d %f%% %f');
NUM_ENTRY = length(data{1});
NUM_TRIAL = data{1}(end) + 1;
ENTRY_PER_TRIAL = NUM_ENTRY / NUM_TRIAL;

trial = 1;
range = trial * ENTRY_PER_TRIAL + 1 : (trial + 1) * ENTRY_PER_TRIAL;
x = data{2}(range);
y_correctness = data{3}(range);
y_confidence = data{4}(range);

figure;
[hAx,hLine1,hLine2] = plotyy(x, y_correctness, x, y_confidence);
title(sprintf('Test Result (Trial %d)', trial));
xlabel('# (Input Tuples)');
ylabel(hAx(1),'Correctness (%)') % left y-axis
ylabel(hAx(2),'Confidence')      % right y-axis
xlim(hAx(1), [0 x(end)]);
xlim(hAx(2), [0 x(end)]);
ylim(hAx(1), [80 100]);
ylim(hAx(2), [0 2000]);

set(gcf, 'PaperUnits', 'points');
set(gcf, 'PaperPosition', [0 0 450 250]);
saveas(gcf, 'plot/trial_1.png');

fclose(fileID);


