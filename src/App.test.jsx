/* eslint no-undef: 0 */
import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
// jest.mock('./api');
import App from './App';


test('The whole thing renders without crashing', () => {
  render(<App />);
});
