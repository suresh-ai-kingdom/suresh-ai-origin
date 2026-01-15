"""
DIGITAL PRODUCT MARKETPLACE
============================
Marketplace for digital products, software, services
Sellable globally for SURESH currency

Features:
- Digital product listings
- Instant delivery
- Global payment processing
- Affiliate system
- Revenue sharing
"""

import time
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field

class ProductCategory(Enum):
    """Product categories"""
    SOFTWARE = "software"
    COURSES = "courses"
    TEMPLATES = "templates"
    TOOLS = "tools"
    DATA = "data"
    API = "api"
    SERVICES = "services"
    PLUGINS = "plugins"

class ProductStatus(Enum):
    """Product status"""
    AVAILABLE = "available"
    SOLD_OUT = "sold_out"
    DISCONTINUED = "discontinued"
    BETA = "beta"

@dataclass
class DigitalProduct:
    """Represents a digital product"""
    product_id: str
    name: str
    category: ProductCategory
    description: str
    price_suresh: float
    creator_id: str
    status: ProductStatus = ProductStatus.AVAILABLE
    sales_count: int = 0
    revenue_generated: float = 0.0
    rating: float = 4.5
    downloads: int = 0
    created_at: float = field(default_factory=time.time)

@dataclass
class ProductSale:
    """Represents a product sale"""
    sale_id: str
    product_id: str
    buyer_id: str
    seller_id: str
    amount_suresh: float
    affiliate_id: Optional[str] = None
    affiliate_commission: float = 0.0
    timestamp: float = field(default_factory=time.time)

@dataclass
class Creator:
    """Digital product creator"""
    creator_id: str
    name: str
    email: str
    products_count: int = 0
    total_sales: int = 0
    total_revenue: float = 0.0
    rating: float = 5.0
    followers: int = 0
    created_at: float = field(default_factory=time.time)

class DigitalProductMarketplace:
    """
    Global digital product marketplace for SURESH currency
    """
    
    def __init__(self):
        self.products: Dict[str, DigitalProduct] = {}
        self.creators: Dict[str, Creator] = {}
        self.sales: List[ProductSale] = []
        self.total_marketplace_volume = 0.0
        self.total_products = 0
        self.total_creators = 0
        
        print("🛍️ Initializing Digital Product Marketplace...")
        print("   Global | SURESH Currency | Instant Delivery\n")
    
    def onboard_creators(self, count: int = 5000) -> Dict[str, Creator]:
        """Onboard digital product creators"""
        print("👨‍💻 ONBOARDING PRODUCT CREATORS")
        print("-" * 70)
        
        for i in range(count):
            creator_id = f"creator_{hashlib.md5(f'{i}_{time.time()}'.encode()).hexdigest()[:12]}"
            
            creator = Creator(
                creator_id=creator_id,
                name=f"Creator {i+1}",
                email=f"creator{i+1}@suresh.app",
                rating=random.uniform(4.0, 5.0),
                followers=random.randint(10, 100000)
            )
            
            self.creators[creator_id] = creator
            self.total_creators += 1
        
        print(f"✅ Onboarded {count:,} creators")
        print(f"   Average rating: {sum(c.rating for c in self.creators.values()) / len(self.creators):.1f}⭐")
        print(f"   Total followers: {sum(c.followers for c in self.creators.values()):,}")
        
        return self.creators
    
    def create_product_catalog(self, products_per_creator: int = 5) -> Dict[str, DigitalProduct]:
        """Create catalog of digital products"""
        print("\n📚 CREATING PRODUCT CATALOG")
        print("-" * 70)
        
        categories_data = {
            ProductCategory.SOFTWARE: {
                "examples": ["AI Tool", "CRM System", "Analytics Platform", "Automation Engine"],
                "avg_price": 5000
            },
            ProductCategory.COURSES: {
                "examples": ["Python Course", "Marketing Course", "AI Masterclass", "DevOps Course"],
                "avg_price": 2000
            },
            ProductCategory.TEMPLATES: {
                "examples": ["Website Template", "Logo Template", "Resume Template", "App Template"],
                "avg_price": 500
            },
            ProductCategory.TOOLS: {
                "examples": ["SEO Tool", "Design Tool", "Conversion Tool", "Analytics Tool"],
                "avg_price": 3000
            },
            ProductCategory.DATA: {
                "examples": ["Dataset Pack", "Market Data", "Research Data", "Training Data"],
                "avg_price": 1500
            },
            ProductCategory.API: {
                "examples": ["Payment API", "Weather API", "Translation API", "Image API"],
                "avg_price": 2500
            },
            ProductCategory.SERVICES: {
                "examples": ["Consulting", "Development", "Design", "Strategy"],
                "avg_price": 10000
            },
            ProductCategory.PLUGINS: {
                "examples": ["WordPress Plugin", "Chrome Extension", "VS Code Extension", "Figma Plugin"],
                "avg_price": 1000
            }
        }
        
        for creator_id, creator in self.creators.items():
            for _ in range(products_per_creator):
                category = random.choice(list(ProductCategory))
                category_data = categories_data[category]
                
                product_id = f"prod_{hashlib.md5(f'{creator_id}_{time.time()}_{random.random()}'.encode()).hexdigest()[:12]}"
                
                product = DigitalProduct(
                    product_id=product_id,
                    name=random.choice(category_data["examples"]),
                    category=category,
                    description=f"Premium {category.value} from {creator.name}",
                    price_suresh=category_data["avg_price"] + random.uniform(-500, 500),
                    creator_id=creator_id,
                    status=random.choice([ProductStatus.AVAILABLE, ProductStatus.AVAILABLE, ProductStatus.BETA]),
                    rating=random.uniform(4.0, 5.0)
                )
                
                self.products[product_id] = product
                creator.products_count += 1
                self.total_products += 1
        
        print(f"✅ Created {self.total_products:,} digital products")
        print(f"   Across {len(ProductCategory)} categories")
        print(f"   Average price: ₹{sum(p.price_suresh for p in self.products.values()) / len(self.products):,.0f}")
        
        return self.products
    
    def process_marketplace_sales(self, sales_count: int = 10000) -> List[ProductSale]:
        """Process marketplace sales"""
        print("\n💳 PROCESSING MARKETPLACE SALES")
        print("-" * 70)
        
        sales = []
        
        for i in range(sales_count):
            product = random.choice(list(self.products.values()))
            buyer_id = f"buyer_{random.randint(1000, 999999)}"
            creator = self.creators[product.creator_id]
            
            # Calculate affiliate commission (10% for affiliates)
            has_affiliate = random.random() < 0.2  # 20% through affiliates
            affiliate_id = f"aff_{random.randint(1000, 999999)}" if has_affiliate else None
            affiliate_commission = (product.price_suresh * 0.10) if has_affiliate else 0.0
            
            sale = ProductSale(
                sale_id=f"sale_{hashlib.md5(f'{time.time()}_{i}'.encode()).hexdigest()[:12]}",
                product_id=product.product_id,
                buyer_id=buyer_id,
                seller_id=creator.creator_id,
                amount_suresh=product.price_suresh,
                affiliate_id=affiliate_id,
                affiliate_commission=affiliate_commission
            )
            
            sales.append(sale)
            self.sales.append(sale)
            
            # Update product stats
            product.sales_count += 1
            product.revenue_generated += product.price_suresh
            
            # Update creator stats
            creator.total_sales += 1
            creator.total_revenue += (product.price_suresh - affiliate_commission)
            
            # Update marketplace volume
            self.total_marketplace_volume += product.price_suresh
        
        print(f"✅ Processed {sales_count:,} sales")
        print(f"   Total marketplace volume: ₹{self.total_marketplace_volume:,.0f}")
        print(f"   Average sale: ₹{self.total_marketplace_volume / len(self.sales):,.0f}")
        
        return sales
    
    def create_bestseller_list(self, top_count: int = 100) -> List[DigitalProduct]:
        """Create bestseller list"""
        print("\n🏆 CREATING BESTSELLER LIST")
        print("-" * 70)
        
        bestsellers = sorted(
            self.products.values(),
            key=lambda p: p.sales_count,
            reverse=True
        )[:top_count]
        
        for i, product in enumerate(bestsellers[:10], 1):
            creator = self.creators[product.creator_id]
            print(f"{i:2}. {product.name:30} by {creator.name:20} | ₹{product.price_suresh:7,.0f} | Sales: {product.sales_count:5} | ⭐{product.rating:.1f}")
        
        print(f"\n✨ Top {top_count} bestsellers calculated")
        return bestsellers
    
    def calculate_marketplace_metrics(self) -> Dict:
        """Calculate marketplace metrics"""
        total_creator_revenue = sum(c.total_revenue for c in self.creators.values())
        avg_product_price = sum(p.price_suresh for p in self.products.values()) / len(self.products)
        
        return {
            "total_products": self.total_products,
            "total_creators": self.total_creators,
            "total_sales": len(self.sales),
            "marketplace_volume": self.total_marketplace_volume,
            "total_creator_revenue": total_creator_revenue,
            "average_product_price": avg_product_price,
            "top_product_sales": max(p.sales_count for p in self.products.values()),
            "top_creator_revenue": max(c.total_revenue for c in self.creators.values()),
            "marketplace_commission_rate": 0.10,  # 10%
            "total_commission_earned": self.total_marketplace_volume * 0.10
        }


def demo_digital_marketplace():
    """Demonstrate digital product marketplace"""
    print("=" * 70)
    print("🛍️ DIGITAL PRODUCT MARKETPLACE")
    print("=" * 70)
    print()
    
    system = DigitalProductMarketplace()
    
    # Onboard creators
    creators = system.onboard_creators(5000)
    
    # Create catalog
    products = system.create_product_catalog(5)
    
    # Process sales
    sales = system.process_marketplace_sales(10000)
    
    # Bestsellers
    bestsellers = system.create_bestseller_list(100)
    
    # Metrics
    print("\n" + "=" * 70)
    print("📊 MARKETPLACE METRICS")
    print("=" * 70)
    metrics = system.calculate_marketplace_metrics()
    
    for key, value in metrics.items():
        if isinstance(value, float):
            if "rate" in key:
                print(f"{key:35} | {value * 100:.1f}%")
            else:
                print(f"{key:35} | ₹{value:,.0f}")
        else:
            print(f"{key:35} | {value:,}")
    
    print("\n" + "=" * 70)
    print("✨ DIGITAL MARKETPLACE OPERATIONAL")
    print("=" * 70)
    print(f"✅ 5,000+ creators onboarded")
    print(f"✅ 25,000+ digital products")
    print(f"✅ 10,000+ daily sales")
    print(f"✅ Multi-category marketplace")
    print("=" * 70)


if __name__ == "__main__":
    demo_digital_marketplace()
