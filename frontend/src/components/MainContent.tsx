import * as React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Toolbar from '@mui/material/Toolbar';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import {useTheme} from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import {drawerWidth} from '../constants';
import axios from 'axios';
import Grid from '@mui/material/Grid';
import {HoldingsItem} from '../App';


interface PortfolioItem {
    symbol: string;
    shares: string;
}

interface MainContentProps {
    setHoldings: React.Dispatch<React.SetStateAction<HoldingsItem[]>>;
}


export const MainContent: React.FC<MainContentProps> = ({setHoldings}) => {
    const [symbol, setSymbol] = React.useState('');
    const [shares, setShares] = React.useState('');
    const [portfolio, setPortfolio] = React.useState<PortfolioItem[]>([]);



    const handleAdd = async () => {
    const newPortfolio = [...portfolio, { symbol, shares }];
    //console.log('New Portfolio Item:', { symbol, shares }); // Log the new portfolio item
    //console.log('Updated Portfolio:', newPortfolio); // Log the entire updated portfolio
    setPortfolio(newPortfolio);


    try {
        //console.log('Sending POST request with portfolio:', newPortfolio); // Log the data being sent in the POST request
        const response = await axios.post('https://fund-breakdown-backend.onrender.com/data', { portfolio: newPortfolio });
        //console.log('Response from server:', response.data); // Log the response from the server
        setHoldings(response.data.holdings);
    } catch (error) {
        //console.error('Error while sending POST request:', error); // Log any errors that occur
    }

    setSymbol('');
    setShares('');
};



    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

    return (
        <Box
            component="main"
            sx={{
                flexGrow: 1,
                p: 3,
                width: {sm: `calc(100% - ${drawerWidth}px)`},
                ml: {sm: `${drawerWidth}px`},
            }}
        >
            <Toolbar/>
            <Box
                display="flex"
                flexDirection={isMobile ? 'column' : 'row'}
                alignItems="center"
                justifyContent={isMobile ? 'center' : 'flex-start'}
            >
                <TextField
                    required
                    id="symbol-field"
                    label="Symbol"
                    variant="filled"
                    value={symbol}
                    sx={{mr: 2}}
                    onChange={(e) => setSymbol(e.target.value)}
                />
                <TextField
                    required
                    id="shares-field"
                    label="Shares"
                    variant="filled"
                    value={shares}
                    sx={{mr: 2}}
                    onChange={(e) => setShares(e.target.value)}
                />
                <Box
                    display="flex"
                    justifyContent={isMobile ? 'center' : 'flex-start'}
                    width="100%"
                >
                    <Button
                        variant="outlined"
                        onClick={handleAdd}
                        size="large"
                        sx={{mt: 1}}
                    >
                        Add
                    </Button>
                </Box>
            </Box>
            <Grid container spacing={2} sx={{mt: 2}}>
                {portfolio.map((item, index) => (
                    <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
                        <Card>
                            <CardContent>
                                <Typography variant="h5">{item.symbol}</Typography>
                                <Typography variant="body2">{item.shares} shares</Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
};