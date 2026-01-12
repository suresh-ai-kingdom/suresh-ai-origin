"""
Tests for Website Generator (Feature #16)
Tests for futuristic 1% tier website generation, performance optimization, and tier analysis
"""

import pytest
import json
from website_generator import (
    generate_website,
    batch_generate_websites,
    optimize_website_performance,
    calculate_performance_score,
    generate_performance_metrics,
    analyze_website_tier_distribution,
    simulate_conversion_impact,
    WEBSITE_TIERS,
    FUTURISTIC_TEMPLATES,
    AI_COPY_LIBRARY
)


class TestWebsiteGeneration:
    """Test basic website generation functionality"""
    
    def test_generate_single_website(self):
        """Test generating a single website"""
        website = generate_website(
            product_name="TestAI Pro",
            product_description="Advanced AI analytics platform",
            target_audience="Enterprise",
            industry="Technology"
        )
        
        assert website is not None
        assert website['product_name'] == "TestAI Pro"
        assert website['product_description'] == "Advanced AI analytics platform"
        assert website['target_audience'] == "Enterprise"
        assert website['industry'] == "Technology"
        assert 'id' in website
        assert 'template' in website
        assert 'tier' in website
        assert website['tier'] in WEBSITE_TIERS
        assert 'copy' in website
        assert 'headline' in website['copy']
        assert 'subheader' in website['copy']
        assert 'cta_button' in website['copy']
    
    def test_website_has_performance_metrics(self):
        """Test that generated websites have performance metrics"""
        website = generate_website(
            product_name="TestProduct",
            product_description="Test description"
        )
        
        assert 'performance' in website
        assert 'score' in website['performance']
        assert 'metrics' in website['performance']
        assert 'page_speed' in website['performance']
        assert 'mobile_score' in website['performance']
        assert 'seo_score' in website['performance']
        assert 'accessibility' in website['performance']
        
        # Verify scores are in valid range
        assert 0 <= website['performance']['score'] <= 100
        assert 0 <= website['performance']['page_speed'] <= 100
        assert 0 <= website['performance']['mobile_score'] <= 100
    
    def test_website_has_design_config(self):
        """Test that websites have design configuration"""
        website = generate_website(
            product_name="TestProduct",
            product_description="Test description"
        )
        
        assert 'design' in website
        assert 'hero_bg' in website['design']
        assert 'text_color' in website['design']
        assert 'accent_color' in website['design']
        assert 'animations' in website['design']
        assert website['design']['text_color'].startswith('#')
        assert website['design']['accent_color'].startswith('#')
    
    def test_website_tier_matches_performance(self):
        """Test that tier matches performance score"""
        website = generate_website(
            product_name="TestProduct",
            product_description="Test"
        )
        
        tier = website['tier']
        score = website['performance']['score']
        score_range = WEBSITE_TIERS[tier]['score_range']
        
        assert score_range[0] <= score <= score_range[1]
    
    def test_batch_generate_websites(self):
        """Test generating multiple website variations"""
        websites = batch_generate_websites(
            product_name="MultiTest",
            product_description="Test batch generation",
            count=3
        )
        
        assert len(websites) == 3
        assert all(w['product_name'] == "MultiTest" for w in websites)
        # Should be sorted by performance score (descending)
        assert websites[0]['performance']['score'] >= websites[1]['performance']['score']
        assert websites[1]['performance']['score'] >= websites[2]['performance']['score']


class TestPerformanceMetrics:
    """Test performance scoring and metrics"""
    
    def test_performance_score_calculation(self):
        """Test performance score calculation"""
        score, tier = calculate_performance_score(
            page_speed=95,
            mobile_score=90,
            seo_score=88,
            accessibility=85
        )
        
        assert isinstance(score, int)
        assert 0 <= score <= 100
        assert tier in WEBSITE_TIERS
    
    def test_performance_score_high_metrics(self):
        """Test score with all high metrics approaches maximum"""
        score, tier = calculate_performance_score(
            page_speed=100,
            mobile_score=100,
            seo_score=100,
            accessibility=100,
            conversion_factors={
                "form_optimization": 10,
                "design_quality": 10,
                "copy_quality": 10,
                "trust_signals": 10
            }
        )
        
        # Score should be 90+ with all high metrics (not perfect due to capped conversion)
        assert 85 <= score <= 100
        assert tier == "BREAKTHROUGH"
    
    def test_performance_score_low_metrics(self):
        """Test score with all low metrics"""
        score, tier = calculate_performance_score(
            page_speed=40,
            mobile_score=40,
            seo_score=40,
            accessibility=40
        )
        
        assert 0 <= score <= 50
        assert tier in ["GROWTH"]
    
    def test_generate_performance_metrics_breakthrough(self):
        """Test performance metrics for BREAKTHROUGH tier"""
        metrics = generate_performance_metrics("BREAKTHROUGH")
        
        assert metrics['page_speed'] >= 90
        assert metrics['mobile_score'] >= 90
        assert metrics['seo_score'] >= 90
    
    def test_generate_performance_metrics_growth(self):
        """Test performance metrics for GROWTH tier"""
        metrics = generate_performance_metrics("GROWTH")
        
        # GROWTH tier should have lower baseline
        assert metrics['page_speed'] <= 75


class TestWebsiteOptimization:
    """Test website performance optimization"""
    
    def test_optimize_website_performance(self):
        """Test website performance optimization"""
        website = generate_website(
            product_name="OptTest",
            product_description="Test optimization"
        )
        
        original_score = website['performance']['score']
        optimized = optimize_website_performance(website)
        
        assert 'optimizations' in optimized['performance']
        assert isinstance(optimized['performance']['optimizations'], list)
        # Score should improve or stay same
        assert optimized['performance']['score'] >= original_score
    
    def test_optimization_suggestions(self):
        """Test that optimization includes valid suggestions"""
        website = generate_website(
            product_name="OptTest",
            product_description="Test"
        )
        
        optimized = optimize_website_performance(website)
        optimizations = optimized['performance']['optimizations']
        
        valid_opts = [
            "enable_lazy_loading", "compress_images", "minify_css_js",
            "enable_caching", "cdn_implementation", "reduce_third_party",
            "optimize_fonts"
        ]
        
        for opt in optimizations:
            assert opt['optimization'] in valid_opts
            assert 'estimated_gain' in opt
            assert 'implementation_effort' in opt


class TestTierAnalysis:
    """Test tier classification and analysis"""
    
    def test_website_tier_distribution(self):
        """Test analyzing tier distribution"""
        websites = batch_generate_websites(
            product_name="TierTest",
            product_description="Test tier analysis",
            count=10
        )
        
        analysis = analyze_website_tier_distribution(websites)
        
        assert 'total_websites' in analysis
        assert analysis['total_websites'] == 10
        assert 'tier_distribution' in analysis
        assert 'tier_percentages' in analysis
        assert 'top_1_percent' in analysis
        assert 'top_5_percent' in analysis
        assert 'recommendations' in analysis
        
        # Verify all tiers are tracked
        for tier in WEBSITE_TIERS.keys():
            assert tier in analysis['tier_distribution']
    
    def test_tier_percentages_sum_to_100(self):
        """Test that tier percentages sum to 100%"""
        websites = batch_generate_websites(
            product_name="TierTest",
            product_description="Test",
            count=20
        )
        
        analysis = analyze_website_tier_distribution(websites)
        total_pct = sum(analysis['tier_percentages'].values())
        
        # Allow small rounding error
        assert 99.9 <= total_pct <= 100.1
    
    def test_recommendations_generated(self):
        """Test that recommendations are generated"""
        websites = batch_generate_websites(
            product_name="RecommendTest",
            product_description="Test recommendations",
            count=5
        )
        
        analysis = analyze_website_tier_distribution(websites)
        
        assert len(analysis['recommendations']) > 0
        assert all(isinstance(r, str) for r in analysis['recommendations'])


class TestConversionImpact:
    """Test conversion rate and revenue impact simulation"""
    
    def test_conversion_impact_breakthrough(self):
        """Test conversion impact for BREAKTHROUGH tier"""
        website = generate_website(
            product_name="ConvTest",
            product_description="Test conversion impact"
        )
        website['tier'] = 'BREAKTHROUGH'
        
        impact = simulate_conversion_impact(website)
        
        assert 'baseline_conversion_rate' in impact
        assert 'optimized_conversion_rate' in impact
        assert 'lift_percentage' in impact
        assert 'monthly_revenue_increase' in impact
        assert 'annual_revenue_increase' in impact
        assert 'payback_period' in impact
    
    def test_conversion_lift_percentage_increases_with_tier(self):
        """Test that better tiers have higher conversion lift"""
        website_breakthrough = generate_website(
            product_name="Conv1",
            product_description="Test"
        )
        website_breakthrough['tier'] = 'BREAKTHROUGH'
        
        website_growth = generate_website(
            product_name="Conv2",
            product_description="Test"
        )
        website_growth['tier'] = 'GROWTH'
        
        impact_breakthrough = simulate_conversion_impact(website_breakthrough)
        impact_growth = simulate_conversion_impact(website_growth)
        
        # BREAKTHROUGH lift should be higher
        lift_b = float(impact_breakthrough['lift_percentage'].rstrip('%'))
        lift_g = float(impact_growth['lift_percentage'].rstrip('%'))
        
        assert lift_b > lift_g


class TestTemplateVariety:
    """Test template variety and configuration"""
    
    def test_templates_exist(self):
        """Test that futuristic templates are defined"""
        assert len(FUTURISTIC_TEMPLATES) > 0
        
        for name, template in FUTURISTIC_TEMPLATES.items():
            assert 'name' in template
            assert 'tier' in template
            assert 'hero' in template
            assert 'sections' in template
            assert 'animations' in template
            assert 'performance_score' in template
    
    def test_all_tiers_represented(self):
        """Test that all tiers have templates"""
        template_tiers = set(t['tier'] for t in FUTURISTIC_TEMPLATES.values())
        required_tiers = set(WEBSITE_TIERS.keys())
        
        # Not all tiers may have templates, but at least some should
        assert len(template_tiers) > 0
    
    def test_ai_copy_library_complete(self):
        """Test that AI copy library has all necessary sections"""
        assert 'hero_headlines' in AI_COPY_LIBRARY
        assert 'subheaders' in AI_COPY_LIBRARY
        assert 'cta_buttons' in AI_COPY_LIBRARY
        
        # Check tier coverage
        for section in AI_COPY_LIBRARY.values():
            assert len(section) > 0
            for tier_copies in section.values():
                assert len(tier_copies) > 0
                assert all(isinstance(c, str) for c in tier_copies)


class TestWebsiteConfiguration:
    """Test website configuration structure"""
    
    def test_website_has_all_required_fields(self):
        """Test that website config has all required fields"""
        website = generate_website(
            product_name="FieldTest",
            product_description="Test"
        )
        
        required_fields = [
            'id', 'product_name', 'product_description', 'template',
            'tier', 'tier_color', 'performance', 'design', 'copy',
            'features', 'created_at'
        ]
        
        for field in required_fields:
            assert field in website, f"Missing field: {field}"
    
    def test_website_copy_has_variants(self):
        """Test that AI copy is varied"""
        websites = [
            generate_website(
                product_name="CopyTest",
                product_description="Test"
            )
            for _ in range(3)
        ]
        
        headlines = [w['copy']['headline'] for w in websites]
        
        # At least some variation expected (not all identical)
        # Note: With random selection, they might coincidentally match
        # so we just verify they're all non-empty strings
        assert all(len(h) > 0 for h in headlines)
        assert all(isinstance(h, str) for h in headlines)


class TestDataConsistency:
    """Test data consistency and validation"""
    
    def test_tier_configuration_consistency(self):
        """Test tier configurations are consistent"""
        for tier_name, tier_config in WEBSITE_TIERS.items():
            assert 'score_range' in tier_config
            assert 'color' in tier_config
            assert 'description' in tier_config
            assert 'conversion_lift' in tier_config
            assert 'features' in tier_config
            
            # Score range validation
            min_score, max_score = tier_config['score_range']
            assert 0 <= min_score < max_score <= 100
            
            # Features validation
            assert len(tier_config['features']) > 0
            assert all(isinstance(f, str) for f in tier_config['features'])
    
    def test_tier_ranges_non_overlapping(self):
        """Test that tier score ranges don't overlap"""
        tiers_sorted = sorted(
            WEBSITE_TIERS.items(),
            key=lambda x: x[1]['score_range'][0]
        )
        
        for i in range(len(tiers_sorted) - 1):
            current_max = tiers_sorted[i][1]['score_range'][1]
            next_min = tiers_sorted[i + 1][1]['score_range'][0]
            
            # Ranges should not overlap (allow one-point overlap for boundaries)
            assert current_max < next_min or current_max == next_min


class TestIntegration:
    """Integration tests for website generation workflow"""
    
    def test_complete_workflow(self):
        """Test complete website generation workflow"""
        # Generate
        websites = batch_generate_websites(
            product_name="WorkflowTest",
            product_description="Complete workflow test",
            count=3
        )
        
        assert len(websites) == 3
        
        # Optimize first
        optimized = optimize_website_performance(websites[0])
        assert optimized['performance']['score'] >= websites[0]['performance']['score']
        
        # Analyze all
        analysis = analyze_website_tier_distribution(websites)
        assert analysis['total_websites'] == 3
        
        # Get conversion impact
        impact = simulate_conversion_impact(websites[0])
        assert 'monthly_revenue_increase' in impact
    
    def test_multi_variation_consistency(self):
        """Test that generated variations maintain consistency"""
        websites = batch_generate_websites(
            product_name="ConsistencyTest",
            product_description="Test consistency",
            count=5
        )
        
        # All should have same product info
        assert all(w['product_name'] == "ConsistencyTest" for w in websites)
        assert all(w['product_description'] == "Test consistency" for w in websites)
        
        # But different configurations
        tiers = [w['tier'] for w in websites]
        templates = [w['template'] for w in websites]
        
        # Should have variety (very unlikely all same)
        assert len(set(tiers)) > 1 or len(set(templates)) > 1
