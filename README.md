# Pyomo + Nextmv: From Local Model to Cloud-Native Optimization

This repository demonstrates how to evolve a basic Pyomo optimization model into a fully-featured, cloud-native application using Nextmv. We'll take you through three stages of development, showing how minimal changes unlock powerful capabilities like observability, collaboration, instance management, version control, and experimentation.

## The Journey: Three Stages of Evolution

### 🏠 Stage 1: Basic Local Pyomo Model (`starting-state/`)

A standard Pyomo diet optimization model that runs locally:

```bash
cd starting-state/
python main.py
```

**What you get:**

- ✅ Working optimization model
- ✅ Local execution
- ❌ No version control
- ❌ No collaboration features  
- ❌ No observability
- ❌ No experimentation

### ☁️ Stage 2: Run in Nextmv (`run_in_nextmv_state/`)

**Changes made:**

1. **Added `app.yaml` manifest** - Tells Nextmv how to run your model

```bash
cd run_in_nextmv_state/
tar czf - diet.dat | nextmv app run -a pyomo-example 
nextmv app output -a pyomo-example -r <insert runID here>
```

**What you unlock:**

- ✅ **Observability**: Detailed execution logs and metrics
- ✅ **Collaboration**: Share apps with team members
- ✅ **Instance Management**: Deploy and manage app versions
- ✅ **Version Control**: Track model changes over time
- ✅ **Cloud Execution**: Run on Nextmv's optimized infrastructure

### 🧪 Stage 3: Full Experimentation Platform (`final_state/`)

**Additional changes:**

1. **Added statistics output** - For experiment tracking and comparison
2. **Exposed options in `app.yaml`** - For model configuration

```bash
cd final_state/
tar czf - diet.dat | nextmv app run -a pyomo-example -o "solver=highs,limit_dairy=true"
nextmv app output -a pyomo-example -r <insert runID here>
```

**What you unlock:**

- ✅ **Configuration Testing**: Compare different solver configurations
- ✅ **Parameter Sweeps**: Test multiple scenarios automatically
- ✅ **Performance Analytics**: Track solution quality and runtime
- ✅ **Business Metrics**: Custom statistics for your domain

## The Model: Diet Optimization

This is a classic optimization problem that minimizes the cost of a diet while meeting nutritional requirements:

- **Objective**: Minimize total cost of food
- **Constraints**:
  - Meet minimum nutritional requirements (calories, protein, vitamins, etc.)
  - Stay within maximum volume limit
  - Optional: Limit dairy products (experimentation feature)

**Foods available**: Cheeseburger, Ham Sandwich, Hamburger, Fish Sandwich, Chicken Sandwich, Fries, Sausage Biscuit, Lowfat Milk, Orange Juice

## Key Changes Explained

### The Minimal App Manifest (`app.yaml`)

```yaml
type: python
runtime: ghcr.io/nextmv-io/runtime/pyomo:latest
python:
  pip-requirements: requirements.txt
files:
  - main.py
  - diet.py
configuration:
  content:
    format: "multi-file"
    multi-file:
      input:
        path: "."
      output:
        solutions: "."
        statistics: "statistics.json"
```

This tells Nextmv:

- Use the Pyomo-optimized runtime
- Include your Python files
- How to handle input/output data

### Adding Experimentation Capabilities

1. **Statistics Output** (`main.py`):

```python
import nextmv

statistics = nextmv.Statistics(
    result=nextmv.ResultStatistics(
        value=value(instance.cost),
        custom={
            "nvars": len(instance.x),
            "nconstraints": len(instance.nutrient_limit) + 1,
        },
    ),
)
```

2. **Configurable Options** (`app.yaml`):

```yaml
configuration:
  options:
    items:
      - name: solver
        option_type: string
        ui:
          control_type: select
        additional_attributes:
          values: [cbc, glpk, highs]
      - name: limit_dairy
        option_type: bool
        default: false
        ui:
          control_type: toggle
```

## Running the Examples

### Prerequisites

### Local Execution

```bash
pip install -r requirements.txt
python main.py

```

### Deploy to Nextmv Cloud

```bash
python push.py
```

## The Power of This Approach

With just two simple changes (adding `app.yaml` and renaming to `main.py`), you transform a local script into a cloud-native optimization application with:

- **Zero infrastructure management**
- **Built-in experiment tracking**
- **Team collaboration features**
- **Automatic scaling**
- **Version control and rollback**
- **Performance monitoring**

This is the power of "Nextmvifying" your optimization models - minimal changes, maximum impact.
