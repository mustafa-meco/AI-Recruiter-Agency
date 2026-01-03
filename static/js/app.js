document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('uploadForm');
    const fileInput = document.getElementById('dropzone-file');
    const fileNameDisplay = document.getElementById('fileName');
    const resultsArea = document.getElementById('resultsArea');
    const submitBtn = form.querySelector('button[type="submit"]');

    // File Input Handler
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = e.target.files[0].name;
            fileNameDisplay.classList.remove('hidden');
        }
    });

    // Form Submit Handler
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI Loading State
        setLoading(true);
        resultsArea.classList.add('hidden');

        const formData = new FormData(form);

        try {
            const response = await fetch('/api/candidate/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                renderResults(data);
                resultsArea.classList.remove('hidden');
                // Smooth scroll to results
                resultsArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                alert('Analysis failed: ' + (data.error || 'Unknown error'));
            }

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        const btnText = document.getElementById('btnText');
        const btnIcon = document.getElementById('btnIcon');
        const btnSpinner = document.getElementById('btnSpinner');

        if (isLoading) {
            btnText.textContent = 'Analyzing...';
            btnIcon.classList.add('hidden');
            btnSpinner.classList.remove('hidden');
            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-75', 'cursor-not-allowed');
        } else {
            btnText.textContent = 'Analyze Profile';
            btnIcon.classList.remove('hidden');
            btnSpinner.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.classList.remove('opacity-75', 'cursor-not-allowed');
        }
    }

    function renderResults(data) {
        // 1. Render Profile Stats
        const profile = data.profile;
        const statsHtml = `
            <div class="bg-slate-900/50 p-4 rounded-xl border border-slate-700">
                <div class="text-slate-400 text-xs uppercase">Experience</div>
                <div class="text-xl font-bold text-white">${profile.years_of_experience || 'N/A'} Yrs</div>
            </div>
            <div class="bg-slate-900/50 p-4 rounded-xl border border-slate-700">
                <div class="text-slate-400 text-xs uppercase">Level</div>
                <div class="text-xl font-bold text-white">${profile.experience_level || 'N/A'}</div>
            </div>
            <div class="bg-slate-900/50 p-4 rounded-xl border border-slate-700 col-span-2">
                <div class="text-slate-400 text-xs uppercase">Latest Role</div>
                <div class="text-lg font-bold text-white truncate">${profile.education?.field || 'Unknown'}</div> 
            </div>
        `;
        document.getElementById('profileStats').innerHTML = statsHtml;

        // 2. Render Skills
        const skillsContainer = document.getElementById('skillTags');
        skillsContainer.innerHTML = (profile.technical_skills || [])
            .map(skill => `<span class="px-3 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-full text-sm font-medium">${skill}</span>`)
            .join('');

        // 3. Render Advice
        const advice = data.advice;
        const adviceHtml = `
            <div class="mb-4">
                <div class="flex items-center gap-2 mb-2">
                    <i class="fa-solid fa-check-circle text-green-500"></i>
                    <span class="font-bold text-white">Strengths</span>
                </div>
                <ul class="list-disc list-inside text-sm pl-2 space-y-1">
                    ${(advice.strengths || []).slice(0, 3).map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
            <div class="mb-4">
                <div class="flex items-center gap-2 mb-2">
                    <i class="fa-solid fa-arrow-trend-up text-blue-500"></i>
                    <span class="font-bold text-white">Actionable Tips</span>
                </div>
                <ul class="list-disc list-inside text-sm pl-2 space-y-1">
                    ${(advice.actionable_tips || []).slice(0, 3).map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
            <div class="mt-4 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-xl">
                <p class="text-sm italic text-yellow-200">"${advice.career_advice || 'Keep pushing forward!'}"</p>
            </div>
        `;
        document.getElementById('adviceContent').innerHTML = adviceHtml;

        // 4. Render Jobs
        const jobsContainer = document.getElementById('jobsList');
        if (data.jobs && data.jobs.length > 0) {
            jobsContainer.innerHTML = data.jobs.map(job => `
                <div class="job-card bg-slate-800 rounded-xl p-6 border border-slate-700 relative overflow-hidden group">
                    <div class="absolute top-0 right-0 p-4 opacity-50">
                        <i class="fa-solid ${job.source && job.source.includes('Live') ? 'fa-globe text-blue-400' : 'fa-database text-slate-600'} text-6xl transform rotate-12 translate-x-4 -translate-y-4"></i>
                    </div>
                    <div class="relative z-10">
                        <div class="flex justify-between items-start mb-4">
                            <div>
                                <h3 class="font-bold text-lg text-white mb-1">${job.title.split(' at ')[0]}</h3>
                                <p class="text-slate-400 text-sm">${job.title.split(' at ')[1] || 'Unknown Co'}</p>
                            </div>
                            <span class="px-2 py-1 bg-${parseInt(job.match_score) > 80 ? 'green' : 'yellow'}-500/20 text-${parseInt(job.match_score) > 80 ? 'green' : 'yellow'}-400 text-xs font-bold rounded-lg border border-${parseInt(job.match_score) > 80 ? 'green' : 'yellow'}-500/30">
                                ${job.match_score} Match
                            </span>
                        </div>
                        
                        <div class="flex gap-4 mb-4 text-sm text-slate-500">
                             <span class="flex items-center gap-1"><i class="fa-solid fa-location-dot"></i> ${job.location}</span>
                             <span class="flex items-center gap-1"><i class="fa-solid fa-money-bill"></i> ${job.salary_range}</span>
                        </div>

                        <div class="pt-4 border-t border-slate-700/50">
                             <div class="flex flex-wrap gap-2">
                                 ${(job.requirements || []).slice(0, 3).map(r => `<span class="text-xs px-2 py-1 bg-slate-900 rounded text-slate-400">${r}</span>`).join('')}
                             </div>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            jobsContainer.innerHTML = `
                <div class="col-span-full text-center py-12 text-slate-500">
                    <i class="fa-solid fa-magnifying-glass text-4xl mb-4 opacity-50"></i>
                    <p>No suitable jobs found matching your profile.</p>
                </div>
            `;
        }
    }
});
