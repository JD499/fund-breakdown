import * as React from 'react';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';

import {drawerWidth} from '../constants';
import Grid from '@mui/material/Grid';

interface HoldingsItem {
    name: string;
    weighting: number;
    price: number;
    value: number;
}

interface HoldingsDisplayProps {
    holdings: HoldingsItem[];
}

export const HoldingsDisplay: React.FC<HoldingsDisplayProps> = ({holdings}) => {
    return (
        <Box
            component="main"
            sx={{
                flexGrow: 1,
                p: 3,
                width: {sm: `calc(100% - ${drawerWidth}px)`},
                ml: {sm: `${drawerWidth}px`},
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
                                '&:hover': {boxShadow: 5}
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