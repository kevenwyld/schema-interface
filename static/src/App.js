import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link
} from "react-router-dom";

import Home from "./template/Home";
import Viewer from "./template/Viewer";

import Button from '@mui/material/Button';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';

import IconButton from '@mui/material/IconButton';
import GitHubIcon from '@mui/icons-material/GitHub';
import HelpIcon from '@mui/icons-material/Help';

import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import './App.scss';

const theme = createTheme({
  palette: {
    primary: {
      light: '#757ce8',
      main: '#3f50b5',
      dark: '#002884',
      contrastText: '#fff',
    },
    secondary: {
      light: '#ff7961',
      main: '#f44336',
      dark: '#ba000d',
      contrastText: '#000',
    },
  },
});

export default function App() {
  return (
    <Router>
      <ThemeProvider theme={theme}>
        <AppBar position="static">
          <Toolbar className="menu">
            <Typography
              variant="h1"
              noWrap
              component="div"
              sx={{ flexGrow: 1, display: { xs: 'none', sm: 'block' } }}
            >
              <Button component={Link} to="/" color="inherit">Schema Curation Interface</Button>
            </Typography>
            <Typography
              variant="body1"
              noWrap
              component="div"
              sx={{ mt: 1, mr: 4 }}
            >
              <Button component={Link} to="/viewer">Viewer</Button>
            </Typography>
            <IconButton
              size="large"
              edge="start"
              color="inherit"
              sx={{ mr: 2 }}
            >
              <a target="_blank" rel="noopener" href="https://github.com/cu-clear/schema-interface">
                <GitHubIcon />
              </a>
            </IconButton>
            <IconButton
              size="large"
              edge="start"
              color="inherit"
              sx={{ mr: 2 }}
            >
              <a target="_blank" rel="noopener" href="https://chrysographes.notion.site/Schema-Curation-Manual-c17f79c7450246d3ad7796e43bebea1b">
                <HelpIcon />
              </a>
            </IconButton>
          </Toolbar>
        </AppBar>
      </ThemeProvider>

      <Routes>
        <Route exact path="/" element={<Home />} />
        <Route exact path="/viewer" element={<Viewer />} />
      </Routes>
    </Router>
  )
}