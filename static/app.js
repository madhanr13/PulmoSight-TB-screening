const fileInput = document.querySelector('#fileInput');
const dropZone = document.querySelector('#dropZone');
const uploadPrompt = document.querySelector('#uploadPrompt');
const previewWrap = document.querySelector('#previewWrap');
const previewImage = document.querySelector('#previewImage');
const fileName = document.querySelector('#fileName');
const fileSize = document.querySelector('#fileSize');
const analyzeButton = document.querySelector('#analyzeButton');
const clearButton = document.querySelector('#clearButton');
let selectedFile = null;

function setFile(file) {
  if (!file || !file.type.startsWith('image/')) return;
  selectedFile = file;
  previewImage.src = URL.createObjectURL(file);
  fileName.textContent = file.name;
  fileSize.textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB · Ready`;
  uploadPrompt.classList.add('hidden');
  previewWrap.classList.remove('hidden');
  analyzeButton.disabled = false;
}

fileInput.addEventListener('change', event => setFile(event.target.files[0]));
['dragenter', 'dragover'].forEach(type => dropZone.addEventListener(type, event => {
  event.preventDefault();
  uploadPrompt.classList.add('dragging');
}));
['dragleave', 'drop'].forEach(type => dropZone.addEventListener(type, event => {
  event.preventDefault();
  uploadPrompt.classList.remove('dragging');
}));
dropZone.addEventListener('drop', event => setFile(event.dataTransfer.files[0]));
clearButton.addEventListener('click', () => {
  selectedFile = null;
  fileInput.value = '';
  previewWrap.classList.add('hidden');
  uploadPrompt.classList.remove('hidden');
  analyzeButton.disabled = true;
});

analyzeButton.addEventListener('click', async () => {
  if (!selectedFile) return;
  analyzeButton.disabled = true;
  analyzeButton.innerHTML = 'Analyzing <span>...</span>';
  const formData = new FormData();
  formData.append('image', selectedFile);
  try {
    const response = await fetch('/api/predict', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Analysis failed');
    document.querySelector('#resultEmpty').classList.add('hidden');
    document.querySelector('#resultContent').classList.remove('hidden');
    document.querySelector('#modelMode').textContent = data.mode;
    document.querySelector('#resultBadge').textContent = data.status === 'positive' ? 'REVIEW ADVISED' : 'SCREENING RESULT';
    document.querySelector('#prediction').textContent = data.prediction;
    document.querySelector('#scoreNumber').innerHTML = `${data.score}<small>%</small>`;
    document.querySelector('#confidenceBar').style.width = `${data.confidence}%`;
    document.querySelector('#confidenceText').textContent = `${data.confidence}%`;
    document.querySelector('#thresholdText').textContent = `${data.threshold}%`;
    document.querySelector('#disclaimer').textContent = data.disclaimer;
  } catch (error) {
    window.alert(error.message);
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.innerHTML = 'Analyze radiograph <span>→</span>';
  }
});
