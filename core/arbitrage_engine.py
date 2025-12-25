"""
Arbitrage Engine Module

This module implements a cryptocurrency arbitrage detection and execution engine
with proper type hints, comprehensive logging, error handling, and realistic
profit calculations.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from enum import Enum
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArbitrageStatus(Enum):
    """Enumeration for arbitrage opportunity status."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExchangeRate:
    """Represents an exchange rate between two assets."""
    exchange: str
    asset_pair: str
    bid_price: Decimal
    ask_price: Decimal
    timestamp: datetime
    volume: Decimal
    
    def __post_init__(self):
        """Validate exchange rate data after initialization."""
        if self.bid_price <= 0 or self.ask_price <= 0:
            raise ValueError("Prices must be positive values")
        if self.bid_price > self.ask_price:
            raise ValueError("Bid price cannot be greater than ask price")
        if self.volume <= 0:
            raise ValueError("Volume must be a positive value")
    
    @property
    def spread(self) -> Decimal:
        """Calculate the bid-ask spread."""
        return self.ask_price - self.bid_price
    
    @property
    def spread_percentage(self) -> Decimal:
        """Calculate spread as a percentage of mid-price."""
        mid_price = (self.bid_price + self.ask_price) / 2
        return (self.spread / mid_price) * 100


@dataclass
class ArbitrageOpportunity:
    """Represents a detected arbitrage opportunity."""
    asset_pair: str
    buy_exchange: str
    buy_price: Decimal
    buy_fee: Decimal  # Fee percentage (e.g., 0.1 for 0.1%)
    sell_exchange: str
    sell_price: Decimal
    sell_fee: Decimal  # Fee percentage
    volume: Decimal
    timestamp: datetime
    status: ArbitrageStatus = ArbitrageStatus.PENDING
    
    def __post_init__(self):
        """Validate arbitrage opportunity data."""
        if self.buy_price <= 0 or self.sell_price <= 0:
            raise ValueError("Prices must be positive values")
        if self.buy_fee < 0 or self.sell_fee < 0:
            raise ValueError("Fees cannot be negative")
        if self.buy_fee >= 100 or self.sell_fee >= 100:
            raise ValueError("Fees cannot be 100% or more")
        if self.volume <= 0:
            raise ValueError("Volume must be a positive value")
    
    @property
    def gross_profit(self) -> Decimal:
        """Calculate gross profit before fees."""
        return (self.sell_price - self.buy_price) * self.volume
    
    @property
    def buy_cost_with_fees(self) -> Decimal:
        """Calculate total cost including buy fees."""
        return self.buy_price * self.volume * (1 + self.buy_fee / 100)
    
    @property
    def sell_revenue_after_fees(self) -> Decimal:
        """Calculate revenue after sell fees."""
        return self.sell_price * self.volume * (1 - self.sell_fee / 100)
    
    @property
    def net_profit(self) -> Decimal:
        """Calculate net profit after all fees."""
        return self.sell_revenue_after_fees - self.buy_cost_with_fees
    
    @property
    def profit_percentage(self) -> Decimal:
        """Calculate profit as a percentage of investment."""
        if self.buy_cost_with_fees == 0:
            return Decimal(0)
        return (self.net_profit / self.buy_cost_with_fees) * 100
    
    @property
    def is_profitable(self) -> bool:
        """Check if the arbitrage opportunity is profitable."""
        return self.net_profit > 0


class ArbitrageConfig:
    """Configuration for arbitrage engine parameters."""
    
    def __init__(
        self,
        min_profit_percentage: Decimal = Decimal("0.5"),
        min_profit_absolute: Decimal = Decimal("10"),
        max_transaction_cost: Decimal = Decimal("1000"),
        max_volume: Decimal = Decimal("100"),
        execution_timeout: int = 30,
    ):
        """
        Initialize arbitrage configuration.
        
        Args:
            min_profit_percentage: Minimum profit percentage required (default: 0.5%)
            min_profit_absolute: Minimum absolute profit required (default: $10)
            max_transaction_cost: Maximum cost per transaction (default: $1000)
            max_volume: Maximum volume to trade (default: 100 units)
            execution_timeout: Timeout for execution in seconds (default: 30)
        """
        self.min_profit_percentage = min_profit_percentage
        self.min_profit_absolute = min_profit_absolute
        self.max_transaction_cost = max_transaction_cost
        self.max_volume = max_volume
        self.execution_timeout = execution_timeout
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration parameters."""
        if self.min_profit_percentage < 0:
            raise ValueError("Minimum profit percentage cannot be negative")
        if self.min_profit_absolute < 0:
            raise ValueError("Minimum absolute profit cannot be negative")
        if self.max_transaction_cost <= 0:
            raise ValueError("Maximum transaction cost must be positive")
        if self.max_volume <= 0:
            raise ValueError("Maximum volume must be positive")
        if self.execution_timeout <= 0:
            raise ValueError("Execution timeout must be positive")


class ArbitrageEngine:
    """
    Main arbitrage detection and execution engine.
    
    This engine detects arbitrage opportunities between different exchanges
    and manages their execution with proper risk management.
    """
    
    def __init__(self, config: Optional[ArbitrageConfig] = None):
        """
        Initialize the arbitrage engine.
        
        Args:
            config: ArbitrageConfig instance (uses defaults if not provided)
        """
        self.config = config or ArbitrageConfig()
        self.opportunities: List[ArbitrageOpportunity] = []
        self.exchange_rates: Dict[str, List[ExchangeRate]] = {}
        logger.info("Arbitrage engine initialized with config: %s", 
                   self._config_to_dict())
    
    def _config_to_dict(self) -> Dict:
        """Convert configuration to dictionary for logging."""
        return {
            "min_profit_percentage": float(self.config.min_profit_percentage),
            "min_profit_absolute": float(self.config.min_profit_absolute),
            "max_transaction_cost": float(self.config.max_transaction_cost),
            "max_volume": float(self.config.max_volume),
            "execution_timeout": self.config.execution_timeout,
        }
    
    def add_exchange_rate(self, rate: ExchangeRate) -> None:
        """
        Add an exchange rate to the engine.
        
        Args:
            rate: ExchangeRate instance to add
            
        Raises:
            ValueError: If rate validation fails
        """
        try:
            if rate.asset_pair not in self.exchange_rates:
                self.exchange_rates[rate.asset_pair] = []
            
            self.exchange_rates[rate.asset_pair].append(rate)
            logger.debug("Added exchange rate: %s on %s at %s", 
                        rate.asset_pair, rate.exchange, rate.ask_price)
        except ValueError as e:
            logger.error("Failed to add exchange rate: %s", str(e))
            raise
    
    def detect_opportunities(
        self, 
        asset_pair: str,
        buy_fee: Decimal,
        sell_fee: Decimal
    ) -> List[ArbitrageOpportunity]:
        """
        Detect arbitrage opportunities for a given asset pair.
        
        Args:
            asset_pair: Trading pair (e.g., 'BTC/USD')
            buy_fee: Buying fee percentage
            sell_fee: Selling fee percentage
            
        Returns:
            List of detected ArbitrageOpportunity instances
        """
        opportunities = []
        
        if asset_pair not in self.exchange_rates:
            logger.warning("No exchange rates found for %s", asset_pair)
            return opportunities
        
        rates = self.exchange_rates[asset_pair]
        
        # Check all pairs of exchanges
        for i, buy_rate in enumerate(rates):
            for sell_rate in rates[i + 1:]:
                # Try both directions
                for _buy, _sell in [(buy_rate, sell_rate), (sell_rate, buy_rate)]:
                    try:
                        opportunity = self._create_opportunity(
                            asset_pair,
                            _buy,
                            _sell,
                            buy_fee,
                            sell_fee
                        )
                        
                        if opportunity and self._validate_opportunity(opportunity):
                            opportunities.append(opportunity)
                            logger.info(
                                "Detected arbitrage opportunity: Buy at %s (%.2f) "
                                "Sell at %s (%.2f) - Profit: %.2f%%",
                                opportunity.buy_exchange,
                                opportunity.buy_price,
                                opportunity.sell_exchange,
                                opportunity.sell_price,
                                opportunity.profit_percentage
                            )
                    except ValueError as e:
                        logger.debug("Invalid opportunity: %s", str(e))
                        continue
        
        self.opportunities.extend(opportunities)
        return opportunities
    
    def _create_opportunity(
        self,
        asset_pair: str,
        buy_rate: ExchangeRate,
        sell_rate: ExchangeRate,
        buy_fee: Decimal,
        sell_fee: Decimal
    ) -> Optional[ArbitrageOpportunity]:
        """
        Create an arbitrage opportunity if conditions are met.
        
        Args:
            asset_pair: Trading pair
            buy_rate: Exchange rate for buying
            sell_rate: Exchange rate for selling
            buy_fee: Buying fee percentage
            sell_fee: Selling fee percentage
            
        Returns:
            ArbitrageOpportunity instance or None if not profitable
        """
        if buy_rate.ask_price >= sell_rate.bid_price:
            return None
        
        # Determine volume based on available liquidity
        volume = min(
            buy_rate.volume,
            sell_rate.volume,
            self.config.max_volume
        )
        
        opportunity = ArbitrageOpportunity(
            asset_pair=asset_pair,
            buy_exchange=buy_rate.exchange,
            buy_price=buy_rate.ask_price,
            buy_fee=buy_fee,
            sell_exchange=sell_rate.exchange,
            sell_price=sell_rate.bid_price,
            sell_fee=sell_fee,
            volume=volume,
            timestamp=datetime.utcnow()
        )
        
        return opportunity
    
    def _validate_opportunity(self, opportunity: ArbitrageOpportunity) -> bool:
        """
        Validate if an opportunity meets profitability criteria.
        
        Args:
            opportunity: ArbitrageOpportunity to validate
            
        Returns:
            True if opportunity meets criteria, False otherwise
        """
        # Check if opportunity is profitable
        if not opportunity.is_profitable:
            logger.debug("Opportunity not profitable: %.2f%%", 
                        opportunity.profit_percentage)
            return False
        
        # Check minimum profit percentage
        if opportunity.profit_percentage < self.config.min_profit_percentage:
            logger.debug("Profit %.2f%% below minimum %.2f%%",
                        opportunity.profit_percentage,
                        self.config.min_profit_percentage)
            return False
        
        # Check minimum absolute profit
        if opportunity.net_profit < self.config.min_profit_absolute:
            logger.debug("Net profit %.2f below minimum %.2f",
                        opportunity.net_profit,
                        self.config.min_profit_absolute)
            return False
        
        # Check transaction cost
        if opportunity.buy_cost_with_fees > self.config.max_transaction_cost:
            logger.debug("Transaction cost %.2f exceeds maximum %.2f",
                        opportunity.buy_cost_with_fees,
                        self.config.max_transaction_cost)
            return False
        
        return True
    
    async def execute_opportunity(
        self, 
        opportunity: ArbitrageOpportunity
    ) -> bool:
        """
        Execute an arbitrage opportunity.
        
        Args:
            opportunity: ArbitrageOpportunity to execute
            
        Returns:
            True if execution succeeded, False otherwise
        """
        try:
            opportunity.status = ArbitrageStatus.EXECUTING
            logger.info("Executing arbitrage opportunity: %s", opportunity)
            
            # Simulate execution with timeout
            await asyncio.wait_for(
                self._simulate_execution(opportunity),
                timeout=self.config.execution_timeout
            )
            
            opportunity.status = ArbitrageStatus.COMPLETED
            logger.info("Successfully executed opportunity with %.2f%% profit",
                       opportunity.profit_percentage)
            return True
            
        except asyncio.TimeoutError:
            opportunity.status = ArbitrageStatus.FAILED
            logger.error("Execution timeout for opportunity")
            return False
        except Exception as e:
            opportunity.status = ArbitrageStatus.FAILED
            logger.error("Execution failed: %s", str(e))
            return False
    
    async def _simulate_execution(self, opportunity: ArbitrageOpportunity):
        """Simulate the execution of an opportunity."""
        await asyncio.sleep(0.1)  # Simulate API calls
    
    def get_profitable_opportunities(self) -> List[ArbitrageOpportunity]:
        """
        Get all profitable opportunities sorted by profit percentage.
        
        Returns:
            List of profitable ArbitrageOpportunity instances sorted by profit
        """
        profitable = [
            opp for opp in self.opportunities 
            if opp.is_profitable and opp.status == ArbitrageStatus.PENDING
        ]
        return sorted(
            profitable, 
            key=lambda x: x.profit_percentage, 
            reverse=True
        )
    
    def clear_opportunities(self) -> None:
        """Clear all stored opportunities."""
        self.opportunities.clear()
        logger.info("Cleared all opportunities")
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about detected opportunities.
        
        Returns:
            Dictionary containing statistics
        """
        total = len(self.opportunities)
        profitable = sum(1 for opp in self.opportunities if opp.is_profitable)
        completed = sum(
            1 for opp in self.opportunities 
            if opp.status == ArbitrageStatus.COMPLETED
        )
        
        total_profit = sum(
            opp.net_profit for opp in self.opportunities 
            if opp.status == ArbitrageStatus.COMPLETED
        )
        
        return {
            "total_opportunities": total,
            "profitable_opportunities": profitable,
            "completed_executions": completed,
            "total_profit": float(total_profit),
            "profitability_rate": (
                profitable / total * 100 if total > 0 else 0
            ),
        }
