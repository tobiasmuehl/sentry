import {
  axisLabelFormatter,
  categorizeDuration,
  tooltipFormatter,
} from 'sentry/utils/discover/charts';
import {MINUTE, SECOND} from 'sentry/utils/formatters';

describe('tooltipFormatter()', function () {
  it('formats values', function () {
    const cases = [
      // function, input, expected
      ['count()', 0.1, '0.1'],
      ['avg(thing)', 0.125126, '0.125'],
      ['failure_rate()', 0.66123, '66.12%'],
      ['p50()', 100, '100.00ms'],
      ['p50()', 100.23, '100.23ms'],
      ['p50()', 1200, '1.20s'],
      ['p50()', 86400000, '1.00d'],
    ];
    for (const scenario of cases) {
      expect(tooltipFormatter(scenario[1], scenario[0])).toEqual(scenario[2]);
    }
  });
});

describe('axisLabelFormatter()', function () {
  it('formats values', function () {
    const cases: [string, number, string][] = [
      // type, input, expected
      ['count()', 0.1, '0.1'],
      ['avg(thing)', 0.125126, '0.125'],
      ['failure_rate()', 0.66123, '66%'],
      ['p50()', 100, '100ms'],
      ['p50()', 541, '541ms'],
      ['p50()', 1200, '1s'],
      ['p50()', 60000, '1min'],
      ['p50()', 120000, '2min'],
      ['p50()', 3600000, '1hr'],
      ['p50()', 86400000, '1d'],
    ];
    for (const scenario of cases) {
      expect(axisLabelFormatter(scenario[1], scenario[0])).toEqual(scenario[2]);
    }
  });

  describe('When a duration unit is passed', function () {
    const getAxisLabels = (axisValues: number[], durationUnit: number) => {
      return axisValues.map(value =>
        axisLabelFormatter(value, 'p50()', undefined, durationUnit)
      );
    };
    const getDurationUnit = (axisValues: number[]) => {
      const max = Math.max(...axisValues);
      const min = Math.min(...axisValues);
      return categorizeDuration((max + min) * 0.5);
    };

    it('should not contain duplicate axis labels', function () {
      const axisValues = [40 * SECOND, 50 * SECOND, 60 * SECOND, 70 * SECOND];
      const durationUnit = getDurationUnit(axisValues);
      const labels = getAxisLabels(axisValues, durationUnit);
      expect(labels.length).toBe(new Set(labels).size);
    });

    it('should use the same duration unit', function () {
      const axisValues = [50 * MINUTE, 150 * MINUTE, 250 * MINUTE, 350 * MINUTE];
      const durationUnit = getDurationUnit(axisValues);
      const labels = getAxisLabels(axisValues, durationUnit);
      expect(labels.length).toBe(labels.filter(label => label.endsWith('hr')).length);
    });
  });
});
