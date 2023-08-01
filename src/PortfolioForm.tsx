import { useState } from 'react';
import axios from 'axios';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';

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
      console.log(response.data);  // log the data to the console
      setHoldings(response.data.holdings);  // update the holdings state with the data
    } catch (error) {
      console.error(error);  // log any errors to the console
    }
  };
  
  
  

  return (
    <Box sx={{ '& > :not(style)': { m: 1 } }}>
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
        <Button type="submit" variant="contained" color="primary">
          Submit
        </Button>
      </form>

      {holdings && (
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
                  <TableCell component="th" scope="row">
                    {holding.name}
                  </TableCell>
                  <TableCell align="right">{holding.weighting}</TableCell>
                  <TableCell align="right">{holding.price}</TableCell>
                  <TableCell align="right">{holding.value}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
  
};

export default PortfolioForm;