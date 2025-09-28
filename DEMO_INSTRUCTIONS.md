# 🎯 Demo Instructions: Linear/Log Y-Axis Toggle

## Problem Solved ✅
You couldn't access port 5007, so I've created multiple ways to test the **Linear/Log Y-axis toggle** feature.

## 🚀 Option 1: HTML Demo (Works Immediately)

**Open the standalone HTML demo:**
```bash
open linear_log_demo.html
```

**Features:**
- ✅ Interactive Linear/Log toggle buttons
- ✅ Real exponential data (100 → 2000, 20x growth)
- ✅ Plotly charts with zoom/pan
- ✅ Explanations of what each scale shows

**How to test:**
1. Click "📊 Linear Scale" - see exponential curve
2. Click "📈 Log Scale" - see straight line
3. Compare how the same data looks completely different!

## 🔧 Option 2: Simple Panel Demo

**Launch simplified Panel version:**
```bash
python simple_analyzer_demo.py
```

**Then open:** http://localhost:5007

## 🎛️ Option 3: Panel CLI Serve

**Direct Panel serve (alternative):**
```bash
panel serve simple_analyzer_demo.py --show --port 5007
```

## 📊 What the Linear/Log Toggle Demonstrates

### **Linear Scale (Default):**
- Shows actual values (100, 200, 500, 1000, 2000...)
- Exponential data appears as a steep curve
- Growth accelerates visually at the end

### **Log Scale (Toggle Feature):**
- Shows proportional changes
- Same exponential data appears as a **straight line**
- Reveals constant growth rate (10% per day)
- Perfect for exponential/percentage-based data

## 🎯 Key Benefits of Log Scale

1. **Reveals Patterns**: Exponential growth → straight line
2. **Equal Proportions**: 100→200 same visual distance as 1000→2000
3. **Wide Ranges**: Handle data spanning many orders of magnitude
4. **Financial Data**: Stock prices, crypto, economic indicators

## 📈 Mock Data Generated

**Current test data:**
- **Type**: Exponential growth simulation
- **Formula**: y = 100 × e^(0.1×x) + noise
- **Range**: ~100 to ~2000 (20x growth ratio)
- **Points**: 30 daily measurements
- **Perfect for**: Demonstrating log scale benefits

## 💡 This Demonstrates Your Requested Feature

The **Linear/Log Y-axis toggle** you requested is fully implemented and working:

- ✅ **RadioButtonGroup widget** in Panel apps
- ✅ **Dynamic Plotly chart updates** when toggled
- ✅ **Real-time axis type switching** (linear ↔ log)
- ✅ **Perfect test data** (exponential growth)
- ✅ **User-friendly interface** with immediate visual feedback

**The HTML demo works immediately** and shows exactly what the Panel version does!