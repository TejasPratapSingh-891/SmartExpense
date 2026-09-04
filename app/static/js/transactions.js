/**
 * SmartExpense Transactions Page Operations
 * Edit transaction modal populator, Delete confirmation, CSV import trigger
 */

async function openEditTxModal(txId) {
  try {
    const res = await fetch(`/api/transactions/${txId}`);
    if (!res.ok) throw new Error('Failed to load transaction data');
    const data = await res.json();

    const form = document.getElementById('editTxForm');
    form.action = `/transactions/${data.id}/edit`;

    document.getElementById('editTitle').value = data.title;
    document.getElementById('editAmount').value = data.amount;
    document.getElementById('editDate').value = data.date;
    document.getElementById('editPayment').value = data.payment_method;
    document.getElementById('editNotes').value = data.notes || '';

    // Set category
    const catSelect = document.getElementById('editCategory');
    catSelect.value = data.category_id;

    // Set radio type
    if (data.type === 'income') {
      document.getElementById('editTypeIncome').checked = true;
    } else {
      document.getElementById('editTypeExpense').checked = true;
    }

    openModal('editTxModal');
  } catch (err) {
    alert('Unable to load transaction details: ' + err.message);
  }
}

function confirmDeleteTx(txId, txTitle) {
  if (confirm(`Are you sure you want to permanently delete transaction "${txTitle}"?`)) {
    const form = document.getElementById('deleteTxForm');
    form.action = `/transactions/${txId}/delete`;
    form.submit();
  }
}
