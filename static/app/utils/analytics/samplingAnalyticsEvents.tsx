import {SamplingInnerName} from 'sentry/types/sampling';

type Rule = {
  conditions: SamplingInnerName[] | string[];
  conditions_stringified: string;
  project_id: string;
  sampling_rate: number | null;
};

export type SamplingEventParameters = {
  'sampling.settings.condition.add': {
    conditions: SamplingInnerName[] | string[];
    project_id: string;
  };
  'sampling.settings.get_started': {
    project_id: string;
  };
  'sampling.settings.read_docs': {
    project_id: string;
  };
  'sampling.settings.rule.create': Rule;
  'sampling.settings.rule.delete': Rule;
  'sampling.settings.rule.save': Rule;
  'sampling.settings.rule.update': Rule & {
    old_conditions: Rule['conditions'];
    old_conditions_stringified: string;
    old_sampling_rate: Rule['sampling_rate'];
  };
  'sampling.settings.view': {project_id: string};
};

type SamplingAnalyticsKey = keyof SamplingEventParameters;

export const samplingEventMap: Record<SamplingAnalyticsKey, string> = {
  'sampling.settings.get_started': 'Get Started with Sampling',
  'sampling.settings.read_docs': 'Read Sampling Docs', // fired for all read docs buttons
  'sampling.settings.condition.add': 'Add Sampling Condition',
  'sampling.settings.rule.create': 'Create Sampling Rule',
  'sampling.settings.rule.delete': 'Delete Sampling Rule',
  'sampling.settings.rule.save': 'Save Sampling Rule', // fired for both create and update
  'sampling.settings.rule.update': 'Update Sampling Rule',
  'sampling.settings.view': 'View Sampling Settings',
};
