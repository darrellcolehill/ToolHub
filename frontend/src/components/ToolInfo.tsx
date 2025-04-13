import Typography from '@mui/material/Typography';
import Box from "@mui/material/Box";
import Divider from '@mui/material/Divider';
import Card from "@mui/material/Card";
import CardContent from '@mui/material/CardContent';
import Container from '@mui/material/Container';

function ToolInfo() {
    return (
        <Box sx={{ backgroundColor: '#f5f5f5', minHeight: '100%', minWidth: '100%', py: 4 }}>
            <Container maxWidth="lg">
                <Card elevation={3} sx={{ borderRadius: 2 }}>
                    <CardContent sx={{ p: 4 }}>
                        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                            {toolDefinition.tool.name}
                        </Typography>
                        <Divider sx={{ my: 2 }} />

                        <Typography variant="h6" gutterBottom>Description</Typography>
                        <Typography variant="body1" sx={{ color: 'text.secondary', mb: 2 }}>
                            {toolDefinition.tool.description}
                        </Typography>
                        <Divider sx={{ my: 2 }} />

                        <Typography variant="h6" gutterBottom>Examples</Typography>
                        {toolDefinition.examples.map((example, index) => (
                            <Typography 
                                key={index} 
                                variant="body2" 
                                sx={{ color: 'text.secondary', mb: 1 }}
                            >
                                • {example}
                            </Typography>
                        ))}
                        <Divider sx={{ my: 2 }} />

                        <Typography variant="h6" gutterBottom>Implementation</Typography>
                        <Box
                            component="pre"
                            sx={{
                                backgroundColor: '#1e1e1e',
                                color: '#dcdcdc',
                                fontFamily: 'monospace',
                                fontSize: '0.875rem',
                                p: 2,
                                borderRadius: 1,
                                overflowX: 'auto',
                                whiteSpace: 'pre-wrap',
                                mt: 1,
                            }}
                        >
                            <code>{toolImplementation}</code>
                        </Box>
                    </CardContent>
                </Card>
            </Container>
        </Box>
    );
}



// TODO: delete after testing

var toolDefinition = {
    examples: [
        "Can you get the weather for CITY STATE?",
        "Get the weather for CITY STATE?",
        "What is the weather for CITY STATE?"

    ],
    tool : {
        name: "fetch_weather",
        description: "Fetch the current weather for a given location.",
        parameters: {
            type: "dict",
            required: [
                "location"
            ],
            properties: {
                location: {
                    "type": "string",
                    "description": "The name of the city or coordinates (latitude,longitude) to fetch the weather for."
                },
                units: {
                    "type": "string",
                    "description": "The unit system for temperature (metric for Celsius, imperial for Fahrenheit).",
                    "enum": ["metric", "imperial"],
                    "default": "metric"
                }
            }
        }
    }

}


var toolImplementation = `
import sys


print("Set alarm")

print("Arguments passed to the script:")
for i, arg in enumerate(sys.argv):
    print(f"Arg {i}: {arg}")
`

export default ToolInfo;