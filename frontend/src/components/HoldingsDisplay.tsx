import * as React from 'react';
import { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import axios from 'axios';
import { drawerWidth } from '../constants';
import Grid from '@mui/material/Grid';

interface HoldingsItem {
  name: string;
  weighting: number;
  price: number;
  value: number;
}

export const HoldingsDisplay: React.FC = () => {
  const [holdings, setHoldings] = useState<HoldingsItem[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/return');  // Replace with your server's URL
        setHoldings(response.data.holdings);
      } catch (error) {
        console.error('Error fetching data: ', error);
      }
    };

    fetchData();
  }, []);

  return (
    <Box
    component="main"
    sx={{ 
      flexGrow: 1, 
      p: 3,
      width: { sm: `calc(100% - ${drawerWidth}px)` }, 
      ml: { sm: `${drawerWidth}px` },
      mt: 5
    }}
    >
      <Grid container spacing={2}>
        {holdings.map((item, index) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
            <Card 
              sx={{ 
                mt: 2, 
                ml: 1,
                mr: 1,
                '&:hover': { boxShadow: 5 } 
              }}
            >
              <CardContent>
                <Typography variant="h5" color="primary" gutterBottom>
                  {item.name}
                </Typography>
                <Typography variant="body2">Weighting: {item.weighting}</Typography>
                <Typography variant="body2">Price: {item.price}</Typography>
                <Typography variant="body2">Value: {item.value}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};
