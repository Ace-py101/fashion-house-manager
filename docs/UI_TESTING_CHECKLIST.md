# Fashion House Manager
# UI Testing Checklist

## 1. Application Shell

- [ ] Application loads without template errors
- [ ] Sidebar displays correctly
- [ ] Top bar displays correctly
- [ ] Breadcrumb area displays correctly
- [ ] Main content area renders correctly


## 2. Mobile Navigation

- [ ] Menu button appears on mobile
- [ ] Sidebar opens when menu button is clicked
- [ ] Overlay appears
- [ ] Clicking overlay closes sidebar
- [ ] Clicking sidebar link closes sidebar


## 3. Notification System

Test:

```python
flash("Customer created successfully.", "success")
flash("Phone number already exists.", "error")
flash("Please fill in all required fields.", "warning")

Verify:
[ ] Success notification displays correctly
[ ] Error notification displays correctly
[ ] Warning notification displays correctly
[ ] Toast animation works
[ ] Toast auto-dismisses
[ ] Close button works
4. Forms
Verify:
[ ] Input fields display correctly
[ ] Buttons display correctly
[ ] Required fields are enforced
[ ] Validation messages appear correctly
[ ] Mobile form layout works
5. Tables
Verify:
[ ] Tables fit desktop screens
[ ] Tables scroll correctly on mobile
[ ] Headers remain readable
[ ] Data alignment is correct
6. Dialogs
Verify:
[ ] Confirmation modal opens
[ ] Cancel button closes modal
[ ] Confirm button works
[ ] Escape key closes modal
7. Theme System
Verify:
[ ] theme.css loads
[ ] CSS variables are available
[ ] Existing design remains unchanged
8. JavaScript Modules
Verify:
[ ] script.js loads
[ ] toast.js loads
[ ] module scripts load without errors
Modules:
dashboard.js
customers.js
orders.js
measurements.js
dialogs.js
forms.js
tables.js
Final Phase 2 Status
Before Phase 3:
[ ] No console errors
[ ] No Flask template errors
[ ] No broken navigation
[ ] Mobile layout works
