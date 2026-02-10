#!/usr/bin/env python3
"""
Mr. Car Pricing Logic Engine
Implements the complete pricing model for vehicle valuation and offers
"""

import json
import math


class PricingEngine:
    """
    Pricing engine that calculates:
    1. Market valuation (PRECIO_MERCADO)
    2. Immediate purchase offer (COMPRA_INMEDIATA) 
    3. Consignment liquidation (LIQUIDACION_FINAL)
    """
    
    # Constants from the pricing model
    PURCHASE_MULTIPLIER = 0.52  # 52% of market price
    
    # Consignment thresholds and rates
    CONSIGNMENT_THRESHOLD = 8000000  # $8M CLP
    HIGH_TIER_COMMISSION_RATE = 0.045  # 4.5%
    TAX_IVA_RATE = 0.19  # 19%
    HIGH_TIER_TOTAL_COMMISSION = 0.05355  # 4.5% + (4.5% * 19%) = 5.355%
    LOW_TIER_FIXED_FEE = 428400  # $428,400 CLP
    
    def __init__(self):
        pass
    
    def round_to_hundred_thousand(self, value):
        """Round to nearest hundred thousand (centena de mil)"""
        return round(value / 100000) * 100000
    
    def calculate_immediate_purchase_offer(self, market_price):
        """
        Step 2: Calculate immediate purchase offer
        Formula: PRECIO_MERCADO * 0.52
        Rounded to nearest 100,000
        """
        if not market_price or market_price <= 0:
            return None
        
        offer = market_price * self.PURCHASE_MULTIPLIER
        return self.round_to_hundred_thousand(offer)
    
    def calculate_consignment_liquidation(self, market_price):
        """
        Step 3: Calculate consignment liquidation
        
        If PRECIO_MERCADO > $8M:
            Commission: 4.5% + IVA(19%) = 5.355% total
            Liquidation = PRECIO_MERCADO * (1 - 0.05355)
        
        If PRECIO_MERCADO <= $8M:
            Fixed fee: $428,400
            Liquidation = PRECIO_MERCADO - $428,400
        """
        if not market_price or market_price <= 0:
            return None
        
        if market_price > self.CONSIGNMENT_THRESHOLD:
            # High tier: percentage-based commission
            liquidation = market_price * (1 - self.HIGH_TIER_TOTAL_COMMISSION)
            return int(liquidation)
        else:
            # Low tier: fixed fee
            liquidation = market_price - self.LOW_TIER_FIXED_FEE
            return int(max(0, liquidation))  # Don't go negative
    
    def calculate_pricing(self, market_price):
        """
        Complete pricing calculation
        
        Args:
            market_price: Market valuation in CLP
        
        Returns:
            dict with all pricing components
        """
        if not market_price or market_price <= 0:
            return {
                "success": False,
                "error": "Invalid market price",
                "market_price": None,
                "immediate_offer": None,
                "consignment_liquidation": None
            }
        
        # Calculate all pricing components
        immediate_offer = self.calculate_immediate_purchase_offer(market_price)
        consignment_liquidation = self.calculate_consignment_liquidation(market_price)
        
        # Determine which consignment tier applies
        consignment_type = "PERCENTAGE_BASED" if market_price > self.CONSIGNMENT_THRESHOLD else "FIXED_FEE"
        
        return {
            "success": True,
            "market_price": int(market_price),
            "immediate_offer": immediate_offer,
            "consignment_liquidation": consignment_liquidation,
            "consignment_type": consignment_type,
            "details": {
                "purchase_multiplier": self.PURCHASE_MULTIPLIER,
                "consignment_threshold": self.CONSIGNMENT_THRESHOLD,
                "commission_rate": self.HIGH_TIER_TOTAL_COMMISSION if consignment_type == "PERCENTAGE_BASED" else None,
                "fixed_fee": self.LOW_TIER_FIXED_FEE if consignment_type == "FIXED_FEE" else None
            }
        }
    
    def format_clp(self, amount):
        """Format amount as Chilean Pesos"""
        if amount is None:
            return "No disponible"
        return f"${amount:,.0f}".replace(",", ".")


def main():
    """Test the pricing engine"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pricing_engine.py <market_price>")
        print("Example: python pricing_engine.py 5000000")
        sys.exit(1)
    
    try:
        market_price = float(sys.argv[1])
    except ValueError:
        print("Error: Market price must be a number")
        sys.exit(1)
    
    engine = PricingEngine()
    result = engine.calculate_pricing(market_price)
    
    print("\n" + "="*60)
    print("💰 MR. CAR PRICING ENGINE")
    print("="*60)
    
    if result["success"]:
        print(f"\n📊 Market Price:            {engine.format_clp(result['market_price'])} CLP")
        print(f"💵 Immediate Purchase:      {engine.format_clp(result['immediate_offer'])} CLP")
        print(f"🤝 Consignment Liquidation: {engine.format_clp(result['consignment_liquidation'])} CLP")
        print(f"\n📋 Consignment Type: {result['consignment_type']}")
        
        if result['consignment_type'] == 'PERCENTAGE_BASED':
            print(f"   Commission: {result['details']['commission_rate']*100:.3f}% (4.5% + IVA)")
        else:
            print(f"   Fixed Fee: {engine.format_clp(result['details']['fixed_fee'])} CLP")
    else:
        print(f"\n❌ Error: {result['error']}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
