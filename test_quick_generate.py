"""Quick test of glow website generation"""
from website_generator import generate_and_save_best_website

print("🌟 Generating ultra-premium glow website...")

result = generate_and_save_best_website(
    product_name="Quantum AI Platform",
    product_description="Revolutionary AI platform that transforms business intelligence",
    target_audience="B2B SaaS",
    count=3
)

print("\n✅ SUCCESS! Website Generated:\n")
print(f"   📄 File: {result['html_file']}")
print(f"   🏆 Tier: {result['tier']}")
print(f"   ⚡ Performance Score: {result['performance_score']}/100")
print(f"   📈 Conversion Lift: +{result['conversion_lift']}%")
print(f"   💰 Revenue Impact: {result['estimated_revenue_impact']}")
print(f"   🎨 Template: {result['template']}")

print(f"\n🚀 Open '{result['html_file']}' in your browser to see the magic!")
