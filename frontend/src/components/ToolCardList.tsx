import { Grid, Card} from '@mui/material'
import ToolCard from './ToolCard';
import Box from "@mui/material/Box";
import Typography from '@mui/material/Typography';



function ToolCardList() {
    return (
      <Box sx={{ backgroundColor: '#f5f5f5', py: 4, px: 2, width: '100%'}}>
        <Grid
          container
          spacing={3}
          justifyContent="center"
        >
          <Grid size={12}>
            <Card 
              variant="outlined" 
              sx={{ 
                p: 2, 
                borderRadius: 2, 
                boxShadow: 2,
                backgroundColor: '#fff'
              }}
            >
              <ToolCard toolInfo={toolInfo1} />
            </Card>
          </Grid>
  
          <Grid size={12}>
            <Box 
              sx={{ 
                p: 2, 
                borderRadius: 2, 
                boxShadow: 1, 
                backgroundColor: '#ffffff',
                height: '100%'
              }}
            >
              <Typography variant="h5" gutterBottom>
                Test Area
              </Typography>
              <Typography variant="body2">
                This section could be used for preview, logs, or additional controls.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Box>
    );
  }
  
  export default ToolCardList;
  
// TODO: delete after testing
const toolInfo1 = {
    modified: "Modified on - 10/4/2024",
    name: "fetch_weather",
    examples: [
      "Can you get the weather for CITY STATE"
    ],
    description: "Fetches the weather for a given location"
  };