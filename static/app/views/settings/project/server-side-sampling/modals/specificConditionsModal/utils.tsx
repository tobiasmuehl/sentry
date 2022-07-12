import {t, tct} from 'sentry/locale';
import {
  SamplingConditionLogicalInner,
  SamplingInnerName,
  SamplingInnerOperator,
  SamplingRule,
} from 'sentry/types/sampling';

import {getInnerNameLabel} from '../../utils';

import {Conditions} from './conditions';
import {TruncatedLabel} from './truncatedLabel';

type Condition = React.ComponentProps<typeof Conditions>['conditions'][0];

export function getMatchFieldPlaceholder(category: SamplingInnerName | string) {
  switch (category) {
    case SamplingInnerName.TRACE_USER_ID:
      return t('ex. 4711 (Multiline)');
    case SamplingInnerName.TRACE_USER_SEGMENT:
      return t('ex. paid, common (Multiline)');
    case SamplingInnerName.TRACE_ENVIRONMENT:
      return t('ex. prod, dev');
    case SamplingInnerName.TRACE_RELEASE:
      return t('ex. 1*, [I3].[0-9].*');
    case SamplingInnerName.TRACE_TRANSACTION:
      return t('ex. page-load');
    default:
      return undefined;
  }
}

export function getNewCondition(condition: Condition): SamplingConditionLogicalInner {
  const newValue = (condition.match ?? '')
    .split('\n')
    .filter(match => !!match.trim())
    .map(match => match.trim());

  if (
    condition.category === SamplingInnerName.TRACE_RELEASE ||
    condition.category === SamplingInnerName.TRACE_TRANSACTION
  ) {
    return {
      op: SamplingInnerOperator.GLOB_MATCH,
      name: condition.category,
      value: newValue,
    };
  }

  if (condition.category === SamplingInnerName.TRACE_USER_ID) {
    return {
      op: SamplingInnerOperator.EQUAL,
      name: condition.category,
      value: newValue,
      options: {
        ignoreCase: false,
      },
    };
  }

  return {
    op: SamplingInnerOperator.EQUAL,
    // TODO(sampling): remove the cast
    name: condition.category as
      | SamplingInnerName.TRACE_ENVIRONMENT
      | SamplingInnerName.TRACE_USER_ID
      | SamplingInnerName.TRACE_USER_SEGMENT,
    value: newValue,
    options: {
      ignoreCase: true,
    },
  };
}

const unexpectedErrorMessage = t('An internal error occurred while saving sampling rule');

type ResponseJSONDetailed = {
  detail: string[];
};

type ResponseJSON = {
  dynamicSampling?: {
    rules: Array<Partial<SamplingRule>>;
  };
};

export function getErrorMessage(
  error: {
    responseJSON?: ResponseJSON | ResponseJSONDetailed;
  },
  currentRuleIndex: number
) {
  const detailedErrorResponse = (error.responseJSON as undefined | ResponseJSONDetailed)
    ?.detail;

  if (detailedErrorResponse) {
    // This is a temp solution until we enable error rules again, therefore it does not need translation
    return detailedErrorResponse[0];
  }

  const errorResponse = error.responseJSON as undefined | ResponseJSON;

  if (!errorResponse) {
    return unexpectedErrorMessage;
  }

  const responseErrors = errorResponse.dynamicSampling?.rules[currentRuleIndex] ?? {};

  const [type, _value] = Object.entries(responseErrors)[0];

  if (type === 'sampleRate') {
    return {
      type: 'sampleRate',
      message: t('Ensure this value is a floating number between 0 and 100'),
    };
  }

  return unexpectedErrorMessage;
}

export function getTagKey(condition: Condition) {
  switch (condition.category) {
    case SamplingInnerName.TRACE_RELEASE:
      return 'release';
    case SamplingInnerName.TRACE_ENVIRONMENT:
      return 'environment';
    case SamplingInnerName.TRACE_TRANSACTION:
      return 'transaction';
    default:
      return undefined;
  }
}

export const distributedTracesConditions = [
  SamplingInnerName.TRACE_RELEASE,
  SamplingInnerName.TRACE_ENVIRONMENT,
  SamplingInnerName.TRACE_USER_ID,
  SamplingInnerName.TRACE_USER_SEGMENT,
  SamplingInnerName.TRACE_TRANSACTION,
];

export function generateConditionCategoriesOptions(
  conditionCategories: SamplingInnerName[]
): [SamplingInnerName, string][] {
  const sortedConditionCategories = conditionCategories
    // sort dropdown options alphabetically based on display labels
    .sort((a, b) => getInnerNameLabel(a).localeCompare(getInnerNameLabel(b)));

  // massage into format that select component understands
  return sortedConditionCategories.map(innerName => [
    innerName,
    getInnerNameLabel(innerName),
  ]);
}

export function formatCreateTagLabel(label: string) {
  return tct('Add "[newLabel]"', {
    newLabel: <TruncatedLabel value={label} />,
  });
}
