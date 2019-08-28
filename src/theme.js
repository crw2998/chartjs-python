import { createMuiTheme, responsiveFontSizes } from '@material-ui/core/styles';

const rawTheme = createMuiTheme({
  palette: {
    primary: { main: '#000000' },
    secondary: { main: '#a0a0a0' },
  },
  status: {
    danger: 'red',
  },
});
const theme = responsiveFontSizes(rawTheme);

export default theme;
