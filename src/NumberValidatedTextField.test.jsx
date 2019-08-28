/* eslint no-undef: 0 */
import React from 'react';
import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/extend-expect';

import NumberValidatedTextField from './NumberValidatedTextField';

const elementWithDefault7 = (
  <NumberValidatedTextField
    defaultValue="7"
    onChange={() => {}}
    label="field"
  />
);
const elementWithNoDefault = (
  <NumberValidatedTextField
    defaultValue=""
    onChange={() => {}}
    label="field"
  />
);
const elementWithBadDefault = (
  <NumberValidatedTextField
    defaultValue="t"
    onChange={() => {}}
    label="field"
  />
);
const elementWithNeedsValue = (
  <NumberValidatedTextField
    defaultValue=""
    onChange={() => {}}
    label="field"
    needsValue
  />
);
const elementWithLessThan10 = (
  <NumberValidatedTextField
    defaultValue=""
    onChange={() => {}}
    label="field"
    needsValue
    lowerThan={10}
  />
);
const elementWithGreaterThan10 = (
  <NumberValidatedTextField
    defaultValue=""
    onChange={() => {}}
    label="field"
    needsValue
    higherThan={10}
  />
);
const elementWithGreaterThanWithBadDefault = (
  <NumberValidatedTextField
    defaultValue={9}
    onChange={() => {}}
    label="field"
    needsValue
    higherThan={10}
  />
);

test('Renders with label somewhere', () => {
  const { getByRole, getByText } = render(elementWithDefault7);
  expect(getByText('field')).toBeInTheDocument();
  expect(getByRole('textbox')).toBeInTheDocument();
});

test('Can take input and return it', () => {
  const { getByRole } = render(elementWithNoDefault);
  userEvent.type(getByRole('textbox'), '7');
  expect(getByRole('textbox')).toBeValid();
  expect(getByRole('textbox')).toHaveValue('7');
});

test('Can take floats', () => {
  const { getByRole } = render(elementWithNoDefault);
  userEvent.type(getByRole('textbox'), '7.12');
  expect(getByRole('textbox')).toBeValid();
  expect(getByRole('textbox')).toHaveValue('7.12');
});

test('Bad input shows as invalid', () => {
  const { getByRole } = render(elementWithNoDefault);
  userEvent.type(getByRole('textbox'), 'j6');
  expect(getByRole('textbox')).toBeInvalid();
});

test('Bad default shows as invalid', () => {
  const { getByRole } = render(elementWithBadDefault);
  expect(getByRole('textbox')).toBeInvalid();
});

test('No input shows as invalid with needsValue', () => {
  const { getByRole } = render(elementWithNeedsValue);
  expect(getByRole('textbox')).toBeInvalid();
  userEvent.type(getByRole('textbox'), 'j6');
  expect(getByRole('textbox')).toBeInvalid();
});

test('Less than functionality', () => {
  const { getByRole } = render(elementWithLessThan10);
  userEvent.type(getByRole('textbox'), '9');
  expect(getByRole('textbox')).toBeValid();
  userEvent.type(getByRole('textbox'), '10.1');
  expect(getByRole('textbox')).toBeInvalid();
  userEvent.type(getByRole('textbox'), '10');
  expect(getByRole('textbox')).toBeInvalid();
});

test('Greater than functionality', () => {
  const { getByRole } = render(elementWithGreaterThan10);
  userEvent.type(getByRole('textbox'), '9.1');
  expect(getByRole('textbox')).toBeInvalid();
  userEvent.type(getByRole('textbox'), '10.1');
  expect(getByRole('textbox')).toBeValid();
  userEvent.type(getByRole('textbox'), '10');
  expect(getByRole('textbox')).toBeInvalid();
});

test('Greater than functionality with bad default', () => {
  const { getByRole } = render(elementWithGreaterThanWithBadDefault);
  expect(getByRole('textbox')).toBeInvalid();
  userEvent.type(getByRole('textbox'), '10.1');
  expect(getByRole('textbox')).toBeValid();
});
