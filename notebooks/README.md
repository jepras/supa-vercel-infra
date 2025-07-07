# AI Analysis Notebooks

This directory contains Jupyter notebooks for prototyping and testing the AI email analysis system using OpenRouter.

## Prerequisites

1. **OpenRouter Setup**: Complete the manual setup steps below
2. **Python Environment**: Ensure you have the required packages installed
3. **API Key**: Set your OpenRouter API key in environment variables

## Manual Setup Steps

### 1. Create OpenRouter Account
1. Go to [https://openrouter.ai/](https://openrouter.ai/)
2. Sign up for an account
3. Verify your email address

### 2. Get API Key
1. After logging in, go to your dashboard
2. Navigate to "API Keys" section
3. Create a new API key
4. **Copy the API key** - you'll need this for the environment variables

### 3. Add Billing Method
1. Go to "Billing" section in your OpenRouter dashboard
2. Add a payment method (credit card)
3. Set up spending limits if desired (recommended to start with $10-20 limit)

### 4. Environment Variables Setup
Add these to your `.env` file or Railway environment variables:
```
OPENROUTER_API_KEY=your_api_key_here
AI_MODEL=openai/gpt-4-1106-preview
```

## Notebooks Overview

### 1. `ai_analysis_prototype.ipynb`
**Purpose**: Basic AI email analysis testing
**What it does**:
- Tests OpenRouter connectivity
- Analyzes sample emails for sales opportunities
- Validates AI reasoning and confidence scores
- Saves results for comparison

**Expected Results**: 
- Opportunities: Emails 1, 2, 3, 5, 6, 8 (sales/proposal emails)
- Non-opportunities: Emails 4, 7 (personal/administrative emails)

### 2. `model_comparison.ipynb`
**Purpose**: Compare different OpenRouter models
**What it does**:
- Tests multiple models (GPT-4, Claude, Gemini, Llama)
- Compares accuracy across models
- Analyzes confidence scores
- Provides model recommendations

**Models Tested**:
- `openai/gpt-4-1106-preview` - Latest GPT-4 (highest accuracy, highest cost)
- `openai/gpt-3.5-turbo` - GPT-3.5 (good accuracy, lower cost)
- `anthropic/claude-3-sonnet` - Claude 3 Sonnet (high accuracy, medium cost)
- `google/gemini-pro` - Gemini Pro (good accuracy, lower cost)
- `meta-llama/llama-2-70b-chat` - Llama 2 (decent accuracy, lowest cost)

### 3. `cost_optimization.ipynb`
**Purpose**: Analyze costs and optimization strategies
**What it does**:
- Compares costs across different models
- Estimates monthly costs for production use
- Provides cost optimization recommendations
- Sets up cost monitoring strategies

## Sample Emails

The notebooks use 8 sample emails representing different scenarios:

1. **Follow-up on meeting** - Sales opportunity
2. **Lunch invitation** - Sales opportunity  
3. **Proposal for review** - Sales opportunity
4. **Thanks for coffee** - Personal (not opportunity)
5. **Contract renewal** - Sales opportunity
6. **Question about services** - Sales opportunity
7. **Meeting reminder** - Administrative (not opportunity)
8. **New business opportunity** - Sales opportunity

## Running the Notebooks

### 1. Install Dependencies
```bash
pip install jupyter openai python-dotenv pandas matplotlib seaborn
```

### 2. Test OpenRouter Connection
```bash
python test_openrouter.py
```

### 3. Start Jupyter
```bash
jupyter notebook
```

### 4. Run Notebooks in Order
1. `ai_analysis_prototype.ipynb` - Basic testing
2. `model_comparison.ipynb` - Model comparison
3. `cost_optimization.ipynb` - Cost analysis

## Expected Outcomes

### Day 1-2: Basic Testing
- ✅ AI can classify emails with >80% accuracy
- ✅ OpenRouter connectivity works
- ✅ Sample emails are properly categorized

### Day 3-4: Model Comparison
- ✅ Best performing model identified
- ✅ Accuracy vs cost trade-off analyzed
- ✅ Model recommendations generated

### Day 5-6: Cost Analysis
- ✅ Monthly cost projections calculated
- ✅ Optimization strategies identified
- ✅ Production model selection made

### Day 7: Production Ready
- ✅ Selected model integrated into backend
- ✅ Webhook pipeline connected
- ✅ End-to-end testing completed

## Cost Estimates

Based on 500 emails per month:
- **GPT-4**: ~$15-20/month
- **GPT-3.5**: ~$2-3/month  
- **Claude 3**: ~$8-12/month
- **Gemini Pro**: ~$2-3/month
- **Llama 2**: ~$1-2/month

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `OPENROUTER_API_KEY` is set in environment
   - Check `.env` file or Railway variables

2. **Model Not Available**
   - Some models may require additional setup
   - Check OpenRouter dashboard for model availability

3. **High Costs**
   - Start with GPT-3.5 for testing
   - Set spending limits in OpenRouter dashboard
   - Use shorter prompts to reduce token usage

4. **Poor Accuracy**
   - Try different models
   - Refine prompts
   - Increase sample size

## Next Steps

After completing the notebooks:

1. **Choose Production Model**: Based on accuracy vs cost analysis
2. **Integrate with Backend**: Use selected model in webhook pipeline
3. **Set Up Monitoring**: Implement cost tracking and alerts
4. **Scale Testing**: Test with larger email datasets
5. **Production Deployment**: Deploy AI analysis to production environment

## Files Generated

The notebooks will generate these files:
- `results_*.json` - Analysis results for each model
- `model_comparison_results.json` - Model comparison data
- `cost_analysis_results.json` - Cost analysis data

These files can be used for further analysis and production integration. 