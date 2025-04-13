import * as React from 'react';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';


function ToolCard({ toolInfo }: { toolInfo: any }) {
    console.log("toolInfo", toolInfo);
    return (
      <React.Fragment>
        <CardContent>
          <Typography gutterBottom sx={{ color: 'text.secondary', fontSize: 14 }}>
            {toolInfo.modified}
          </Typography>
          <Typography variant="h5" component="div" sx={{ color: 'text.primary' }}>
            {toolInfo.name}
          </Typography>
          <Typography sx={{ textAlign: 'left', color: 'text.primary', mb: 1.5 }}>
            {toolInfo.description}
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.primary' }}>
            {toolInfo.examples[0]}
          </Typography>
        </CardContent>
        <CardActions>
          <Button size="small">View More</Button>
        </CardActions>
      </React.Fragment>
    );
  }

export default ToolCard;