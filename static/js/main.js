document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('url');
    const evaluateButton = document.getElementById('evaluate');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const loadingDiv = document.getElementById('loading');
    
    // Score elements
    const probabilityBar = document.getElementById('probability-bar');
    const probabilityValue = document.getElementById('probability-value');
    const reachBar = document.getElementById('reach-bar');
    const reachValue = document.getElementById('reach-value');
    const relevanceBar = document.getElementById('relevance-bar');
    const relevanceValue = document.getElementById('relevance-value');
    
    // Content elements
    const categoryText = document.getElementById('category');
    const reasoningText = document.getElementById('reasoning');
    const indicatorsList = document.getElementById('indicators');
    const salesPitchText = document.getElementById('sales-pitch');

    evaluateButton.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        
        if (!url) {
            showError('Please enter a URL');
            return;
        }

        // Reset UI
        hideError();
        hideResult();
        showLoading();

        try {
            console.log('Sending request for URL:', url);
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url }),
            });

            const data = await response.json();
            console.log('Received response:', data);

            if (!response.ok) {
                throw new Error(data.error || data.detail || 'Failed to evaluate URL');
            }

            if (data.error) {
                throw new Error(data.error);
            }

            displayResult(data);
        } catch (error) {
            console.error('Error during evaluation:', error);
            showError(`Error: ${error.message}`);
        } finally {
            hideLoading();
        }
    });

    function displayResult(data) {
        try {
            console.log('Displaying result:', data);
            
            // Validate required data
            if (!data.probability || !data.reachScore || !data.relevanceScore) {
                throw new Error('Missing core score data in response');
            }

            // Update score bars and values
            updateScoreBar(data.probability, 'probability');
            updateScoreBar(data.reachScore, 'reach');
            updateScoreBar(data.relevanceScore, 'relevance');
            
            // Business Profile
            if (data.businessProfile) {
                document.getElementById('industry').textContent = data.businessProfile.industry || 'N/A';
                document.getElementById('company-size').textContent = data.businessProfile.companySize || 'N/A';
                document.getElementById('geographic-reach').textContent = data.businessProfile.geographicReach || 'N/A';
                document.getElementById('years-in-business').textContent = data.businessProfile.yearsInBusiness || 'N/A';
                document.getElementById('portfolio-size').textContent = data.businessProfile.clientPortfolioSize || 'N/A';
            }

            // Technical Assessment
            if (data.technicalAssessment) {
                updateTags('tech-stack', data.technicalAssessment.techStack || []);
                document.getElementById('accessibility-solutions').textContent = data.technicalAssessment.accessibilitySolutions || 'N/A';
                updateStarRating('integration-score', data.technicalAssessment.integrationScore || 0);
                updateTags('dev-services', data.technicalAssessment.developmentServices || []);
                document.getElementById('hosting-services').textContent = data.technicalAssessment.hostingServices || 'N/A';
            }

            // Market Position
            if (data.marketPosition) {
                updateTags('market-segments', data.marketPosition.segments || []);
                updateList('competitors', data.marketPosition.competitors || []);
                const certifications = [
                    ...(data.marketPosition.certifications || []),
                    ...(data.marketPosition.memberships || [])
                ];
                updateTags('certifications', certifications);
                updateList('awards', data.marketPosition.awards || []);
            }

            // Client Relationships
            if (data.clientRelationships) {
                updateTags('client-types', data.clientRelationships.clientTypes || []);
                document.getElementById('avg-client-size').textContent = data.clientRelationships.averageClientSize || 'N/A';
                document.getElementById('retention-rate').textContent = data.clientRelationships.retentionRate || 'N/A';
                document.getElementById('service-model').textContent = data.clientRelationships.serviceModel || 'N/A';
                document.getElementById('success-stories').textContent = data.clientRelationships.successStories || '0';
            }

            // Business Model
            if (data.businessModel) {
                updateTags('revenue-streams', data.businessModel.revenueStreams || []);
                document.getElementById('pricing-model').textContent = data.businessModel.pricingModel || 'N/A';
                document.getElementById('sales-approach').textContent = data.businessModel.salesApproach || 'N/A';
                document.getElementById('service-delivery').textContent = data.businessModel.serviceDelivery || 'N/A';
                updateTags('contract-types', data.businessModel.contractTypes || []);
            }

            // Compliance & Growth
            if (data.complianceGrowth) {
                updateTags('regulatory-focus', data.complianceGrowth.regulatoryFocus || []);
                updateTags('compliance-services', data.complianceGrowth.complianceServices || []);
                updateList('growth-indicators', data.complianceGrowth.growthIndicators || []);
                updateStarRating('digital-presence-score', data.complianceGrowth.digitalPresenceScore || 0);
                updateList('future-plans', data.complianceGrowth.futurePlans || []);
            }

            // Partnership Evaluation
            if (data.partnershipEvaluation) {
                updateList('strengths', data.partnershipEvaluation.strengths || []);
                updateList('challenges', data.partnershipEvaluation.challenges || []);
                updateList('opportunities', data.partnershipEvaluation.opportunities || []);
                updateList('risks', data.partnershipEvaluation.risks || []);
                document.getElementById('recommended-approach').textContent = data.partnershipEvaluation.recommendedApproach || 'N/A';
            }

            // Existing fields
            updateList('indicators', data.indicators || []);
            document.getElementById('sales-pitch').textContent = data.salesPitch || 'N/A';

            resultDiv.classList.remove('hidden');
        } catch (error) {
            console.error('Error displaying result:', error);
            showError(`Error displaying results: ${error.message}`);
        }
    }

    function updateScoreBar(score, prefix) {
        const bar = document.getElementById(`${prefix}-bar`);
        const value = document.getElementById(`${prefix}-value`);
        if (bar && value) {
            bar.style.width = `${score}%`;
            value.textContent = `${score}%`;
        } else {
            console.error(`Could not find elements for ${prefix} score`);
        }
    }

    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }

    function hideError() {
        errorDiv.classList.add('hidden');
    }

    function hideResult() {
        resultDiv.classList.add('hidden');
    }

    function showLoading() {
        loadingDiv.classList.remove('hidden');
        evaluateButton.disabled = true;
    }

    function hideLoading() {
        loadingDiv.classList.add('hidden');
        evaluateButton.disabled = false;
    }

    function updateTags(elementId, items) {
        const container = document.getElementById(elementId);
        container.innerHTML = '';
        items.forEach(item => {
            const tag = document.createElement('span');
            tag.className = 'px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-sm';
            tag.textContent = item;
            container.appendChild(tag);
        });
    }

    function updateList(elementId, items) {
        const container = document.getElementById(elementId);
        container.innerHTML = '';
        items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            container.appendChild(li);
        });
    }

    function updateStarRating(elementId, score) {
        const container = document.getElementById(elementId);
        container.innerHTML = '';
        for (let i = 0; i < 5; i++) {
            const star = document.createElement('svg');
            star.className = `w-5 h-5 ${i < score ? 'text-yellow-400' : 'text-gray-300'}`;
            star.innerHTML = `<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>`;
            container.appendChild(star);
        }
    }
}); 