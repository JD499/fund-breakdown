import * as React from 'react';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import AddchartOutlinedIcon from '@mui/icons-material/AddchartOutlined';
import { TableChartOutlined } from '@mui/icons-material';
import Toolbar from '@mui/material/Toolbar';
import { drawerWidth } from '../constants';
import Box from '@mui/material/Box';
import { Link } from 'react-router-dom';

interface DrawerProps {
  mobileOpen: boolean;
  handleDrawerToggle: () => void;
  window?: () => Window;
}

export const DrawerComponent: React.FC<DrawerProps> = ({ mobileOpen, handleDrawerToggle, window }) => {
  const drawer = (
    <div>
      <Toolbar />
      <Divider />
      <List>
  {['Portfolio', 'Holdings'].map((text, index) => (
    <ListItem key={text} disablePadding>
      <ListItemButton component={Link} to={index % 2 === 0 ? "/" : "/holdings"}>
        <ListItemIcon>
          {index % 2 === 0 ? <AddchartOutlinedIcon /> : <TableChartOutlined />}
        </ListItemIcon>
        <ListItemText primary={text} />
      </ListItemButton>
    </ListItem>
  ))}
</List>
    </div>
  );

  const container = window !== undefined ? () => window().document.body : undefined;

  return (
    <Box
      component="nav"
      sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      aria-label="mailbox folders"
    >
      <Drawer
        container={container}
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
      >
        {drawer}
      </Drawer>
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
        open
      >
        {drawer}
      </Drawer>
    </Box>
  );
};
