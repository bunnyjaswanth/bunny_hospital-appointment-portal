/**
 * Medicare Hospital & Patient Appointment Management Portal
 * Client-Side JavaScript Logic
 */

document.addEventListener('DOMContentLoaded', function () {
    initDoctorFiltering();
    initSlotSelector();
    initAlertAutoDismiss();
});

/**
 * 1. Doctor Filtering by Department & Search Query
 * Covers: Cardiology, Pediatrics, Orthopedics, Neurology, etc.
 */
function initDoctorFiltering() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const doctorCards = document.querySelectorAll('.doctor-card-wrapper');
    const searchInput = document.getElementById('doctorSearchInput');
    const countDisplay = document.getElementById('visibleDoctorCount');

    if (!filterButtons.length && !searchInput) return;

    let currentDept = 'All';
    let currentQuery = '';

    function filterDoctors() {
        let visibleCount = 0;

        doctorCards.forEach(card => {
            const dept = card.getAttribute('data-department') || '';
            const name = card.getAttribute('data-name') || '';
            const spec = card.getAttribute('data-specialization') || '';

            const matchesDept = (currentDept === 'All') || (dept.toLowerCase() === currentDept.toLowerCase());
            const textToSearch = `${name} ${dept} ${spec}`.toLowerCase();
            const matchesQuery = !currentQuery || textToSearch.includes(currentQuery);

            if (matchesDept && matchesQuery) {
                card.style.display = '';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        if (countDisplay) {
            countDisplay.textContent = visibleCount;
        }

        const noResultsAlert = document.getElementById('noDoctorsAlert');
        if (noResultsAlert) {
            noResultsAlert.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    filterButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentDept = this.getAttribute('data-dept') || 'All';
            filterDoctors();
        });
    });

    if (searchInput) {
        searchInput.addEventListener('input', function () {
            currentQuery = this.value.trim().toLowerCase();
            filterDoctors();
        });
    }
}

/**
 * 2. Interactive Appointment Date & Time Slot Selection
 * Queries /api/slots/ endpoint to render booked and available slots
 */
function initSlotSelector() {
    const doctorSelect = document.getElementById('id_doctor');
    const dateInput = document.getElementById('id_date');
    const timeSlotSelect = document.getElementById('id_time_slot');
    const slotContainer = document.getElementById('slotContainer');
    const slotLoading = document.getElementById('slotLoading');
    const slotFeedback = document.getElementById('slotFeedback');
    const doctorFeeBadge = document.getElementById('doctorFeeBadge');
    const doctorDaysBadge = document.getElementById('doctorDaysBadge');

    if (!doctorSelect || !dateInput || !slotContainer) return;

    function fetchAndUpdateSlots() {
        const doctorId = doctorSelect.value;
        const dateVal = dateInput.value;

        if (!doctorId || !dateVal) {
            slotContainer.innerHTML = '<div class="text-center text-muted py-4"><i class="bi bi-calendar-event fs-3 d-block mb-2"></i>Please select a Doctor and Date above to view available time slots.</div>';
            if (slotFeedback) slotFeedback.innerHTML = '';
            return;
        }

        if (slotLoading) slotLoading.style.display = 'block';
        slotContainer.innerHTML = '';

        fetch(`/api/slots/?doctor_id=${encodeURIComponent(doctorId)}&date=${encodeURIComponent(dateVal)}`)
            .then(res => {
                if (!res.ok) throw new Error('Network error loading slots');
                return res.json();
            })
            .then(data => {
                if (slotLoading) slotLoading.style.display = 'none';

                if (doctorFeeBadge && data.consultation_fee) {
                    doctorFeeBadge.textContent = `$${data.consultation_fee}`;
                }
                if (doctorDaysBadge && data.available_days) {
                    doctorDaysBadge.textContent = data.available_days;
                }

                renderSlotButtons(data);
            })
            .catch(err => {
                if (slotLoading) slotLoading.style.display = 'none';
                slotContainer.innerHTML = `<div class="alert alert-warning py-2 mb-0"><i class="bi bi-exclamation-triangle me-2"></i>Could not load live slots: ${err.message}. Please use the dropdown below.</div>`;
            });
    }

    function renderSlotButtons(data) {
        slotContainer.innerHTML = '';
        const allSlots = data.all_slots || [];
        const bookedSlots = new Set(data.booked_slots || []);
        const currentSelectedSlot = timeSlotSelect ? timeSlotSelect.value : '';

        if (allSlots.length === 0) {
            slotContainer.innerHTML = '<p class="text-muted text-center py-2">No slots configured.</p>';
            return;
        }

        const grid = document.createElement('div');
        grid.className = 'slot-grid';

        allSlots.forEach(slot => {
            const isBooked = bookedSlots.has(slot);
            const isSelected = slot === currentSelectedSlot && !isBooked;

            const btn = document.createElement('div');
            btn.className = `slot-btn ${isBooked ? 'booked' : ''} ${isSelected ? 'selected' : ''}`;
            btn.setAttribute('data-slot', slot);

            if (isBooked) {
                btn.innerHTML = `<i class="bi bi-x-circle text-danger"></i> <span>${slot}</span>`;
                btn.title = 'This slot has already been booked. Please pick another time.';
            } else {
                btn.innerHTML = `<i class="bi bi-clock"></i> <span>${slot}</span>`;
                btn.addEventListener('click', function () {
                    document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                    btn.classList.add('selected');

                    if (timeSlotSelect) {
                        timeSlotSelect.value = slot;
                    }

                    if (slotFeedback) {
                        slotFeedback.innerHTML = `<div class="alert alert-success py-2 px-3 mt-2 mb-0 d-flex align-items-center"><i class="bi bi-check-circle-fill me-2 fs-5"></i><div><strong>Selected Slot:</strong> ${slot} on ${data.date}</div></div>`;
                    }
                });
            }

            grid.appendChild(btn);
        });

        slotContainer.appendChild(grid);

        // Summary legend
        const legend = document.createElement('div');
        legend.className = 'd-flex flex-wrap gap-3 mt-3 pt-2 border-top small text-muted';
        legend.innerHTML = `
            <div class="d-flex align-items-center"><span class="badge bg-light text-dark border me-1 px-2 py-1">Available</span> Click to select</div>
            <div class="d-flex align-items-center"><span class="badge bg-primary me-1 px-2 py-1">Selected</span> Chosen slot</div>
            <div class="d-flex align-items-center"><span class="badge bg-danger me-1 px-2 py-1">Booked</span> Unavailable (Reserved)</div>
        `;
        slotContainer.appendChild(legend);

        // If previously selected slot is now booked, reset select
        if (bookedSlots.has(currentSelectedSlot)) {
            if (timeSlotSelect) timeSlotSelect.value = '';
            if (slotFeedback) {
                slotFeedback.innerHTML = `<div class="alert alert-danger py-2 px-3 mt-2 mb-0"><i class="bi bi-exclamation-octagon-fill me-2"></i>The previously chosen slot (${currentSelectedSlot}) is now booked for this doctor. Please pick another available slot.</div>`;
            }
        }
    }

    doctorSelect.addEventListener('change', fetchAndUpdateSlots);
    dateInput.addEventListener('change', fetchAndUpdateSlots);

    // Initial check if values are present (e.g. from prefilled query params)
    if (doctorSelect.value && dateInput.value) {
        fetchAndUpdateSlots();
    }
}

/**
 * 3. Alert auto-dismissal
 */
function initAlertAutoDismiss() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });
}
