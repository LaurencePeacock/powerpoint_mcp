# PowerPoint MCP

This PowerPoint MCP extends the functionality of the python-pptx library such that content can be added to presentations 
via user provided natural language prompts. A small range of custom layout slides have been provided in this example. 

It is intended to solve the following problem:

#### Scenario: 
PowerPoint presentations are created by organisations for a range of use cases, both as part of repeated processs and ad hoc.
#### Aim: 
For users to create organisation-specific presentations more quickly and efficiently via natural language prompts and UI file handling
#### Issues:
Current out-the-box Agents can generate presentations but not with corporate themes and cannot be customised with organisation-specific tools.
#### Solution: 
An Agent / MCP combination that facilitates session based PowerPoint creation and editing

# Local Set Up

1. Use UV to create the virtual environment and install packages:

(If you do not have UV installed, go here: https://docs.astral.sh/uv/getting-started/installation/#standalone-installer
)
```shell
  uv sync
``` 

2. Get a Gemini API Key from https://aistudio.google.com/api-keys

3. Update the .env file, adding the API Key to the GOOGLE_API_KEY variable. (You do not need to update API_KEY)

4. Start the local MCP server:
```shell
  fastmcp run server.py --transport http --host 0.0.0.0 --port 8001 --path /mcp
```
5. Run the Agent in the ADK Web UI:
```shell
  adk web
```
6. Open the provided localhost address and port

7. Select 'agent' from the 'Select an agent' dropdown

8. Start the agent with any prompt and enter a filename when asked

9. Here are some suggested prompts



# User Guide


### Starting the Agent
When you open a new PowerPoint Agent session with ```web adk```, you will need to prompt the Agent to start.

Here are some suggestions: 
> start 

> let's go!

>reveal your secrets!

Whatever prompt you give it, the Agent will ask you for a filename for your Presentation.

### Naming your Presentation
This will be used as the title on the first slide of the Presentation. Only numeric and alphabetic characters are allowed.

### Quick Start Guide

Here are some example prompts that you might like to try now:

> Add this chart data to a new slide and add a summary of the data: 
> 
>Date Revenue (£) Units Sold
> 
>01/01/2023 15200 750
> 
>01/02/2023 14850 730
> 
>01/03/2023 16300 810


Or you might say:

> Make three new slides. 
> 
> On slide one, add this analysis: "lorem ipsum example analsysis". 
> 
> On slide two, add this table with a summary: 
> 
> Product Category	Units Sold	Customer Rating (out of 5)
> 
>Electronics	4500	4.5
> 
>Home & Garden	6200	4.2
> 
>Clothing	8900	3.9
> 
>Books	3100	4.8
> 
>Sports Equipment	2500	4.6
> 
>Toys & Games	4100	4.1. 
> 
> On slide three, add a paragraph drawing conclusions based on the analysis and table.

**Viewing the Presentation**

The presentation is saved in the presentations directory on your local machine


### How do I know what the layouts are?

To see all the available layouts: 
> show layouts

### Editing and Deleting Slides
If you want to edit or delete a slide, you need to know the number of the slide

You can either open the Presentation and take a sneaky peak. Eg. Title slide is slide 1.

Or you can use the prompt:
> Show summary

This will show you something like this:

> Here is a summary of your presentation:
> 
>Total number of slides: 4
> 
> Slide Information:
> 
>Slide 1: Title Slide
> 
>Slide 2: Chart Right Hand with Text on Left
> 
>Slide 3: Right Hand Table with Text Box on Left
> 
>Slide 4: Chart Right Hand with Text on Left

If you want to edit that third slide  that isn't quite right yet:

> I want to edit slide 3. Change the title so it's 'QBR Summary'

This lets the Agent be sure of which slide you want to change.

But what if that slide still isn't right! Let's get rid of and start again

> delete slide 3

## Suggested Prompts

> Add a new slide. Use layout Large Text on Left Hand Side. Add this text: 'lorem ipsum diddly squattum'

> I want to edit slide 4. Change the title to 'Budget Analysis'

>  Add a new slide. use Two Text Columns

> List slide layouts 

>  Add this data as a chart to a new slide and include analysis:
>Date Revenue (£) Units Sold
>01/01/2023 15200 750
01/02/2023 14850 730
01/03/2023 16300 810
01/04/2023 17100 855
01/05/2023 18500 920
01/06/2023 19200 960
01/07/2023 21500 1050
01/08/2023 20800 1025
01/09/2023 18900 940
01/10/2023 19500 975
01/11/2023 22300 1100
01/12/2023 28500 1400
01/01/2024 16100 790
01/02/2024 15900 780
01/03/2024 17500 860
01/04/2024 18200 900

## Adding Tables and Charts

Data that is appropriately formatted can be pasted into the Agent chat box straight from a spreadsheet.

Essentially, if you can turn it into a chart or table in Excel, you're good to go with the Agent.

By default, the agent will generate a chart title

If you want to use your own title, just provide one in the prompt. Or state that no title is required.

By default, charts will be added with a legend. If you do not want a legend, state 'no legend' or something similar.

Currently it will only render bar charts. But it can handle bar charts with multiple columns

It can also handle selecting columns from a larger data set.
Eg:

> Add the first two columns of this data set as a chart:
> 
>Date, Ad Spend, Conversions, ROAS,
> 05/2025, £300, 56, 8.9%
> 06/2025, £500, 46, 6.4%

As you can see from the above, it will also handle empty values.

## Suggested Prompts

#### Example One - Chuck content at it

>Add the following content to the presentation. If you have questions or need more information, ask.
> 
>
>"Introduction: Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos."
>"Lorem ipsum dolor sit amet consectetur adipiscing elit.
>Quisque faucibus ex sapien vitae pellentesque.
>In id cursus mi pretium tellus duis convallis."
>
> Chart - add analysis
>Segment,Market Share Opportunity ($M)
>Segment A,15
>Segment B,22
>Segment C (Untapped),45
>Segment D,18
>
>Table - add analysis
>Metric,Current Market Average,Project Nova Target,Disruption Factor
>Customer Acquisition Cost,$150,$75,50%
>Time to Value,30 days,7 days,77%
>User Engagement,25%,60%,140%
>
>
>"Conclusions: Lorem ipsum dolor sit amet consectetur adipiscing elit.
>Quisque faucibus ex sapien vitae pellentesque.
>In id cursus mi pretium tellus duis convallis."


#### Example Two - Provide a detailed plan

>Add the following content to the presentation. Follow the slide breakdown. If you have questions or need more information, ask.
>
>***SLIDE BREAKDOWN***
>
>Slide 1 - Introduction
>
>Layout: Large Text on Left Hand Side
>
>"Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos."
>
>Slide 2 - Summary
>
>Layout: Large Text on Left Hand Side.
>
>"Lorem ipsum dolor sit amet consectetur adipiscing elit.
> 
>Quisque faucibus ex sapien vitae pellentesque.
>
>In id cursus mi pretium tellus duis convallis."
>
>Slide 3 - Chart One
>
>Layout: Chart Right Hand with Text on Left
>
>Add analysis of chart data:
>
>Segment,Market Share Opportunity ($M)
>Segment A,15
>Segment B,22
>Segment C (Untapped),45
>Segment D,18
>
>Slide 4 - Table One
>
>Layout: Left Hand Table with Text Box on Right 
>
>Add analysis of table data:
>
>Metric,Current Market Average,Project Nova Target,Disruption Factor
>Customer Acquisition Cost,$150,$75,50%
>Time to Value,30 days,7 days,77%
>User Engagement,25%,60%,140%
>
>Slide 5 - Conclusions
>
>Layout: Large Text on Left Hand Side.
>
>"Lorem ipsum dolor sit amet consectetur adipiscing elit.
>
>Quisque faucibus ex sapien vitae pellentesque.
>
>In id cursus mi pretium tellus duis convallis."

