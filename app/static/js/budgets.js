/**
 * SmartExpense Budget Operations
 * Budget adjust modal populator & Delete trigger
 */

function openAdjustBudgetModal(budgetId, catName, catId, currentLimit) {
  document.getElementById('adjustBudgetId').value = budgetId;
  document.getElementById('adjustCatName').textContent = catName;
  document.getElementById('adjustCatId').value = catId;
  document.getElementById('adjustLimit').value = currentLimit;
  openModal('adjustBudgetModal');
}

function confirmDeleteBudget(budgetId, catName) {
  if (confirm(`Remove budget allocation for ${catName}?`)) {
    const form = document.getElementById('deleteBudgetForm');
    form.action = `/budgets/${budgetId}/delete`;
    form.submit();
  }
}
