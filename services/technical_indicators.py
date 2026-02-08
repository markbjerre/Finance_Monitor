"""
Technical Indicators Service - Calculate financial indicators for technical analysis

Includes RSI, MACD, Bollinger Bands, Moving Averages, and other technical indicators
"""

from typing import List, Dict, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_sma(prices: List[float], period: int) -> List[float]:
    """
    Calculate Simple Moving Average (SMA)
    
    Args:
        prices: List of prices
        period: Number of days for moving average
        
    Returns:
        List of SMA values (None for initial period)
    """
    sma = []
    for i in range(len(prices)):
        if i < period - 1:
            sma.append(None)
        else:
            avg = sum(prices[i - period + 1:i + 1]) / period
            sma.append(round(avg, 2))
    return sma


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """
    Calculate Exponential Moving Average (EMA)
    
    Args:
        prices: List of prices
        period: Number of days for moving average
        
    Returns:
        List of EMA values
    """
    ema = []
    multiplier = 2 / (period + 1)
    
    for i in range(len(prices)):
        if i == 0:
            ema.append(prices[i])
        elif i < period - 1:
            ema.append(None)
        else:
            if ema[i - 1] is not None:
                ema_val = (prices[i] - ema[i - 1]) * multiplier + ema[i - 1]
                ema.append(round(ema_val, 2))
            else:
                ema.append(None)
    return ema


def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """
    Calculate Relative Strength Index (RSI)
    Measures momentum and overbought/oversold conditions
    
    Args:
        prices: List of prices
        period: Number of days (default 14)
        
    Returns:
        List of RSI values (0-100)
    """
    rsi_values = []
    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    # Initialize RSI values list with None for initial period
    rsi_values = [None] * period
    
    for i in range(period, len(deltas)):
        if i == period:
            avg_gain = sum(gains[:period]) / period
            avg_loss = sum(losses[:period]) / period
        else:
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            rsi = 100 if avg_gain > 0 else 0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        rsi_values.append(round(rsi, 2))
    
    # Pad with None for initial period
    while len(rsi_values) < len(prices):
        rsi_values.insert(0, None)
    
    return rsi_values[:len(prices)]


def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, List[float]]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        prices: List of prices
        fast: Fast EMA period (default 12)
        slow: Slow EMA period (default 26)
        signal: Signal line period (default 9)
        
    Returns:
        Dict with macd, signal, and histogram
    """
    fast_ema = calculate_ema(prices, fast)
    slow_ema = calculate_ema(prices, slow)
    
    macd_line = []
    for i in range(len(prices)):
        if fast_ema[i] is not None and slow_ema[i] is not None:
            macd_line.append(round(fast_ema[i] - slow_ema[i], 2))
        else:
            macd_line.append(None)
    
    signal_line = calculate_ema(macd_line, signal)
    
    histogram = []
    for i in range(len(macd_line)):
        if macd_line[i] is not None and signal_line[i] is not None:
            histogram.append(round(macd_line[i] - signal_line[i], 2))
        else:
            histogram.append(None)
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


def calculate_bollinger_bands(prices: List[float], period: int = 20, num_std: float = 2) -> Dict[str, List[float]]:
    """
    Calculate Bollinger Bands
    
    Args:
        prices: List of prices
        period: Period for moving average (default 20)
        num_std: Number of standard deviations (default 2)
        
    Returns:
        Dict with upper, middle, lower bands
    """
    sma = calculate_sma(prices, period)
    
    upper_band = []
    middle_band = []
    lower_band = []
    
    for i in range(len(prices)):
        if sma[i] is not None:
            # Calculate standard deviation for this window
            window = prices[i - period + 1:i + 1]
            mean = sma[i]
            variance = sum((x - mean) ** 2 for x in window) / period
            std_dev = variance ** 0.5
            
            middle_band.append(round(sma[i], 2))
            upper_band.append(round(sma[i] + (num_std * std_dev), 2))
            lower_band.append(round(sma[i] - (num_std * std_dev), 2))
        else:
            middle_band.append(None)
            upper_band.append(None)
            lower_band.append(None)
    
    return {
        'upper': upper_band,
        'middle': middle_band,
        'lower': lower_band
    }


def calculate_technical_summary(prices: List[float]) -> Dict[str, Any]:
    """
    Calculate comprehensive technical analysis summary
    
    Args:
        prices: List of historical prices
        
    Returns:
        Dict with all technical indicators and interpretations
    """
    if len(prices) < 30:
        return {'error': 'Insufficient data for technical analysis (need at least 30 days)'}
    
    try:
        # Calculate indicators
        rsi = calculate_rsi(prices, period=14)
        macd = calculate_macd(prices)
        bollinger = calculate_bollinger_bands(prices, period=20)
        sma_20 = calculate_sma(prices, 20)
        sma_50 = calculate_sma(prices, 50)
        ema_12 = calculate_ema(prices, 12)
        
        # Get latest values
        latest_price = prices[-1]
        latest_rsi = rsi[-1]
        latest_macd = macd['macd'][-1]
        latest_signal = macd['signal'][-1]
        latest_histogram = macd['histogram'][-1]
        latest_bb_upper = bollinger['upper'][-1]
        latest_bb_middle = bollinger['middle'][-1]
        latest_bb_lower = bollinger['lower'][-1]
        latest_sma_20 = sma_20[-1]
        latest_sma_50 = sma_50[-1]
        
        # Generate interpretations
        interpretation = {
            'rsi': {
                'value': latest_rsi,
                'status': interpret_rsi(latest_rsi),
                'description': 'Relative Strength Index measures momentum'
            },
            'macd': {
                'value': latest_macd,
                'signal': latest_signal,
                'histogram': latest_histogram,
                'status': interpret_macd(latest_macd, latest_signal),
                'description': 'Moving Average Convergence Divergence'
            },
            'bollinger_bands': {
                'upper': latest_bb_upper,
                'middle': latest_bb_middle,
                'lower': latest_bb_lower,
                'status': interpret_bollinger(latest_price, latest_bb_upper, latest_bb_lower),
                'description': 'Bollinger Bands show volatility and support/resistance'
            },
            'moving_averages': {
                'sma_20': latest_sma_20,
                'sma_50': latest_sma_50,
                'status': interpret_moving_averages(latest_price, latest_sma_20, latest_sma_50),
                'description': 'Moving Averages indicate trend direction'
            },
            'price_position': {
                'current': latest_price,
                'above_bb_upper': latest_price > latest_bb_upper if latest_bb_upper else None,
                'below_bb_lower': latest_price < latest_bb_lower if latest_bb_lower else None
            }
        }
        
        # Overall signal
        signals = [
            interpret_rsi(latest_rsi),
            interpret_macd(latest_macd, latest_signal),
            interpret_bollinger(latest_price, latest_bb_upper, latest_bb_lower),
            interpret_moving_averages(latest_price, latest_sma_20, latest_sma_50)
        ]
        
        bullish_count = sum(1 for s in signals if 'bullish' in s.lower())
        bearish_count = sum(1 for s in signals if 'bearish' in s.lower())
        
        if bullish_count > bearish_count:
            overall_signal = 'Bullish'
        elif bearish_count > bullish_count:
            overall_signal = 'Bearish'
        else:
            overall_signal = 'Neutral'
        
        return {
            'indicators': interpretation,
            'overall_signal': overall_signal,
            'signal_strength': f'{bullish_count} bullish vs {bearish_count} bearish signals',
            'calculated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating technical summary: {e}")
        return {'error': str(e)}


def interpret_rsi(rsi: float) -> str:
    """Interpret RSI value"""
    if rsi is None:
        return 'Insufficient data'
    elif rsi > 70:
        return 'Overbought - Bearish'
    elif rsi < 30:
        return 'Oversold - Bullish'
    else:
        return 'Neutral'


def interpret_macd(macd_val: float, signal_val: float) -> str:
    """Interpret MACD crossover"""
    if macd_val is None or signal_val is None:
        return 'Insufficient data'
    elif macd_val > signal_val:
        return 'Bullish Crossover'
    elif macd_val < signal_val:
        return 'Bearish Crossover'
    else:
        return 'Neutral'


def interpret_bollinger(price: float, upper: float, lower: float) -> str:
    """Interpret Bollinger Bands position"""
    if upper is None or lower is None:
        return 'Insufficient data'
    elif price > upper:
        return 'Overbought - Bearish'
    elif price < lower:
        return 'Oversold - Bullish'
    else:
        return 'Neutral'


def interpret_moving_averages(price: float, sma_20: float, sma_50: float) -> str:
    """Interpret Moving Average trend"""
    if sma_20 is None or sma_50 is None:
        return 'Insufficient data'
    elif sma_20 > sma_50 and price > sma_20:
        return 'Strong Uptrend - Bullish'
    elif sma_20 < sma_50 and price < sma_20:
        return 'Strong Downtrend - Bearish'
    elif price > sma_20:
        return 'Uptrend - Bullish'
    elif price < sma_20:
        return 'Downtrend - Bearish'
    else:
        return 'Neutral'
