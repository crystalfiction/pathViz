import { render, screen } from '@testing-library/react';
import GUI from './GUI';

test('renders learn react link', () => {
  render(<GUI />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
