import { useState } from 'react';
import axios from 'axios';
import { 
  Button, 
  TextField, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  Box,
  Typography,
  Grid,
  Card,
  CardContent
} from '@mui/material';

const PortfolioForm = () => {
  const [symbols, setSymbols] = useState('');
  const [shares, setShares] = useState('');
  const [holdings, setHoldings] = useState<{ name: string, weighting: number, price: number, value: number }[] | null>(null);

  const handleSubmit = async (event: { preventDefault: () => void; }) => {
    event.preventDefault();
  
    const formData = new FormData();
    formData.append('symbols', symbols);
    formData.append('shares', shares);
  
    try {
      const response = await axios.post('http://localhost:5000/', formData);
      setHoldings(response.data.holdings);
    } catch (error) {
      console.error(error);
    }
  };

  const renderTable = () => (
    holdings && (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell align="right">Weighting</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">Value</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {holdings.map((holding, index) => (
              <TableRow key={index}>
                <TableCell component="th" scope="row">{holding.name}</TableCell>
                <TableCell align="right">{holding.weighting}</TableCell>
                <TableCell align="right">{holding.price}</TableCell>
                <TableCell align="right">{holding.value}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    )
  );

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography variant="h4" gutterBottom>
          Portfolio Form
        </Typography>
      </Grid>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <form onSubmit={handleSubmit}>
              <TextField
                id="symbols"
                label="Enter symbols (comma separated)"
                value={symbols}
                onChange={(e) => setSymbols(e.target.value)}
                fullWidth
              />
              <TextField
                id="shares"
                label="Enter shares (comma separated)"
                value={shares}
                onChange={(e) => setShares(e.target.value)}
                fullWidth
              />
              <Button type="submit" variant="contained" color="primary" style={{ marginTop: '10px' }}>
                Submit
              </Button>
            </form>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12}>
        {renderTable()}
      </Grid>
    </Grid>
  );
};

export default PortfolioForm;
