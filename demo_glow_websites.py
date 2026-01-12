"""
🌟 ULTRA-PREMIUM GLOW WEBSITE GENERATOR - DEMO
Generate top 1% websites in seconds!
"""

from website_generator import (
    generate_and_save_best_website,
    generate_website,
    generate_glow_html,
    batch_generate_websites
)
import os

def demo_quick_generation():
    """Quick demo: Generate one premium website"""
    print("=" * 70)
    print("🌟 QUICK DEMO: Generating Ultra-Premium Glow Website")
    print("=" * 70)
    
    result = generate_and_save_best_website(
        product_name="Quantum AI Platform",
        product_description="Revolutionary AI platform that transforms business intelligence",
        target_audience="B2B SaaS",
        count=5  # Generate 5 variations, pick the best
    )
    
    print(f"\n✅ SUCCESS! Website Generated:\n")
    print(f"   📄 File: {result['html_file']}")
    print(f"   🏆 Tier: {result['tier']}")
    print(f"   ⚡ Performance Score: {result['performance_score']}/100")
    print(f"   📈 Conversion Lift: +{result['conversion_lift']}%")
    print(f"   💰 Revenue Impact: {result['estimated_revenue_impact']}")
    print(f"   🎨 Template: {result['template']}")
    print(f"   🔄 Alternatives Generated: {result['alternatives_generated']}")
    
    print(f"\n🚀 Next Step: Open '{result['html_file']}' in your browser!")
    print("=" * 70)
    
    return result


def demo_batch_generation():
    """Generate multiple client websites"""
    print("\n" + "=" * 70)
    print("🎯 BATCH DEMO: Generating Websites for Multiple Clients")
    print("=" * 70)
    
    clients = [
        {
            "name": "CloudSync Pro",
            "description": "Real-time data synchronization for enterprises",
            "audience": "B2B SaaS"
        },
        {
            "name": "FitLife Premium",
            "description": "Personal training and nutrition app",
            "audience": "B2C Health"
        },
        {
            "name": "LegalPro Suite",
            "description": "Complete legal management platform",
            "audience": "B2B Professional Services"
        }
    ]
    
    results = []
    
    for client in clients:
        print(f"\n📦 Generating website for: {client['name']}...")
        
        result = generate_and_save_best_website(
            product_name=client["name"],
            product_description=client["description"],
            target_audience=client["audience"],
            count=3
        )
        
        results.append(result)
        
        print(f"   ✅ {result['tier']} tier (Score: {result['performance_score']})")
        print(f"   💾 Saved: {result['html_file']}")
    
    print("\n" + "=" * 70)
    print(f"🎉 Generated {len(results)} premium websites!")
    print("=" * 70)
    
    return results


def demo_custom_website():
    """Generate a fully customized website"""
    print("\n" + "=" * 70)
    print("🎨 CUSTOM DEMO: Your Custom Website")
    print("=" * 70)
    
    # Get user input
    product_name = input("\n📝 Enter product name (or press Enter for 'My Awesome Product'): ").strip()
    if not product_name:
        product_name = "My Awesome Product"
    
    description = input("📝 Enter product description (or press Enter for default): ").strip()
    if not description:
        description = "Revolutionary platform that changes everything"
    
    print(f"\n🔄 Generating 5 variations for '{product_name}'...")
    
    result = generate_and_save_best_website(
        product_name=product_name,
        product_description=description,
        target_audience="B2B SaaS",
        count=5
    )
    
    print(f"\n✅ Your website is ready!")
    print(f"   📄 File: {result['html_file']}")
    print(f"   🏆 Tier: {result['tier']}")
    print(f"   ⚡ Performance: {result['performance_score']}/100")
    print(f"   📈 Conversion Lift: +{result['conversion_lift']}%")
    
    print(f"\n🌟 Open '{result['html_file']}' in your browser to see your glow website!")
    print("=" * 70)
    
    return result


def demo_show_all_tiers():
    """Show all tier configurations"""
    from website_generator import WEBSITE_TIERS
    
    print("\n" + "=" * 70)
    print("🏆 WEBSITE TIERS - Choose Your Level")
    print("=" * 70)
    
    for tier_name, tier_info in WEBSITE_TIERS.items():
        print(f"\n{tier_name}:")
        print(f"  Color: {tier_info['color']}")
        print(f"  Description: {tier_info['description']}")
        print(f"  Conversion Lift: +{tier_info['conversion_lift']}%")
        print(f"  Features: {', '.join(tier_info['features'])}")
    
    print("\n" + "=" * 70)


def main():
    """Main demo menu"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "   🌟 ULTRA-PREMIUM GLOW WEBSITE GENERATOR   ".center(68) + "║")
    print("║" + "   Generate Top 1% Websites in Seconds!   ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    print("\n📋 DEMO OPTIONS:\n")
    print("   1️⃣  Quick Demo - Generate one premium website")
    print("   2️⃣  Batch Demo - Generate multiple client websites")
    print("   3️⃣  Custom Demo - Create your custom website")
    print("   4️⃣  Show Tiers - View all tier configurations")
    print("   5️⃣  Run All Demos")
    print("   0️⃣  Exit")
    
    choice = input("\n👉 Select option (1-5, or 0 to exit): ").strip()
    
    if choice == "1":
        demo_quick_generation()
    elif choice == "2":
        demo_batch_generation()
    elif choice == "3":
        demo_custom_website()
    elif choice == "4":
        demo_show_all_tiers()
    elif choice == "5":
        demo_show_all_tiers()
        demo_quick_generation()
        demo_batch_generation()
    elif choice == "0":
        print("\n👋 Thanks for using Glow Website Generator!")
        return
    else:
        print("\n❌ Invalid choice. Please select 1-5 or 0.")
        return main()
    
    # Ask if user wants to continue
    again = input("\n🔄 Generate more? (y/n): ").strip().lower()
    if again == 'y':
        main()
    else:
        print("\n🎉 All done! Your glow websites are ready.")
        print("📁 Check your current directory for the HTML files.")
        print("🚀 Open them in a browser to see the magic!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting... Thanks for using Glow Website Generator!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure you're in the correct directory with website_generator.py")
