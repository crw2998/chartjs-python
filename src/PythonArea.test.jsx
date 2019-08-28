/* eslint no-undef: 0 */
import React from 'react';
import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/extend-expect';

import PythonArea from './PythonArea';

jest.mock('./api');
import { requestFunctionUpdate, subscribeToFunctionUpdates, setFunctionUpdateResponse } from './api';

const element = (
  <PythonArea
    handleFunctionUpdate={() => {}}
    errorOverrideData=""
  />
);
const elementWithErrorOverride = (
  <PythonArea
    handleFunctionUpdate={() => {}}
    errorOverrideData={['ErrorOverrideLine1', 'ErrorOverrideLine2']}
  />
);

test('Renders a text area', () => {
  setFunctionUpdateResponse({ error: null, params: [] });
  const { getByRole } = render(element);
  expect(getByRole('textbox')).toBeInTheDocument();
});

test('Returns params correctly from Python', () => {
  let params;
  const passedParamList = ['a', 'b'];
  setFunctionUpdateResponse({ error: null, params: passedParamList });
  const { getByRole } = render(
    <PythonArea
      handleFunctionUpdate={(returnedParams) => {
        params = returnedParams;
      }}
      errorOverrideData=""
    />,
  );
  expect(getByRole('textbox')).toBeInTheDocument();
  expect(params).toEqual(passedParamList);
});

test('Renders errors returned from Python', async () => {
  setFunctionUpdateResponse({ error: ['First Error!', 'Second Line of Error!'] });
  const { getByTestId, findByText } = render(element);
  expect(getByTestId('error-container')).toBeInTheDocument();

  expect(getByTestId('error-container')).toContainElement(await findByText('First Error!'));
  expect(getByTestId('error-container')).toContainElement(await findByText('Second Line of Error!'));
});

test('Uses error override data', async () => {
  setFunctionUpdateResponse({ error: null, params: [] });
  const { getByTestId, findByText } = render(elementWithErrorOverride);
  expect(getByTestId('error-container')).toBeInTheDocument();
  expect(getByTestId('error-container')).toContainElement(await findByText('ErrorOverrideLine1'));
  expect(getByTestId('error-container')).toContainElement(await findByText('ErrorOverrideLine2'));
});

test('Error Override only when error empty', async () => {
  setFunctionUpdateResponse({ error: ['First Error!', 'Second Line of Error!'] });
  const { getByTestId, findByText, getByText } = render(elementWithErrorOverride);
  expect(getByTestId('error-container')).toBeInTheDocument();
  expect(getByTestId('error-container')).toContainElement(await findByText('First Error!'));
  expect(getByTestId('error-container')).toContainElement(await findByText('Second Line of Error!'));

  expect(getByTestId('error-container')).not.toHaveTextContent('ErrorOverrideLine1');
  expect(getByTestId('error-container')).not.toHaveTextContent('ErrorOverrideLine2');
});
