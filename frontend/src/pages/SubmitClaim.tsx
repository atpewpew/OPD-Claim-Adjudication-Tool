import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { claimsApi } from "../api/services";
import { 
  Upload, 
  File, 
  Trash2, 
  ChevronDown, 
  ChevronUp, 
  Loader2, 
  AlertCircle,
  FileCheck2,
  Calendar,
  Building2,
  User,
  DollarSign
} from "lucide-react";

export const SubmitClaim: React.FC = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Form States
  const [memberId, setMemberId] = useState("EMP001");
  const [treatmentDate, setTreatmentDate] = useState(() => {
    return new Date().toISOString().split("T")[0];
  });
  const [claimAmount, setClaimAmount] = useState<number>(0);
  const [hospitalName, setHospitalName] = useState("");
  
  // Additional States
  const [cashlessRequest, setCashlessRequest] = useState(false);
  const [preAuthProvided, setPreAuthProvided] = useState(false);
  const [previousClaimsSameDay, setPreviousClaimsSameDay] = useState(0);

  // Files upload state
  const [files, setFiles] = useState<File[]>([]);
  const [isDragActive, setIsDragActive] = useState(false);

  // UI Control states
  const [showAdditional, setShowAdditional] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitStep, setSubmitStep] = useState(0); // 0: None, 1: OCR, 2: Gemini, 3: Rule engine
  const [error, setError] = useState<string | null>(null);

  // File size formatter
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
  };

  // Drag and drop handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      // Validate file types
      const validTypes = ["application/pdf", "image/jpeg", "image/png", "image/webp"];
      const filteredFiles = droppedFiles.filter(file => {
        const isValid = validTypes.includes(file.type);
        if (!isValid) {
          setError(`File format of "${file.name}" is not supported. Please upload PDF, JPG, PNG or WEBP.`);
        }
        return isValid;
      });

      setFiles(prev => [...prev, ...filteredFiles]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFiles = Array.from(e.target.files);
      setFiles(prev => [...prev, ...selectedFiles]);
      setError(null);
    }
  };

  const removeFile = (indexToRemove: number) => {
    setFiles(prev => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  // Form Submit Handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (files.length === 0) {
      setError("Please upload at least one medical document (prescription/bill) to proceed.");
      return;
    }
    if (claimAmount <= 0) {
      setError("Please enter a valid claim amount greater than ₹0.");
      return;
    }

    setSubmitting(true);
    setError(null);
    setSubmitStep(1);

    // Simulate pipeline steps visually for better feedback
    const stepInterval = setInterval(() => {
      setSubmitStep(prev => {
        if (prev < 3) return prev + 1;
        return prev;
      });
    }, 2800);

    try {
      const formData = new FormData();
      formData.append("member_id", memberId);
      formData.append("treatment_date", treatmentDate);
      formData.append("claim_amount", String(claimAmount));
      formData.append("hospital_name", hospitalName.trim() || "");
      formData.append("cashless_request", String(cashlessRequest));
      formData.append("pre_auth_provided", String(preAuthProvided));
      formData.append("previous_claims_same_day", String(previousClaimsSameDay));
      
      // Append files
      files.forEach(file => {
        formData.append("files", file);
      });

      const claimResponse = await claimsApi.submitClaim(formData);
      clearInterval(stepInterval);
      
      // Navigate to detail page on success
      navigate(`/claim/${claimResponse.claim_id}`);
    } catch (err: any) {
      clearInterval(stepInterval);
      console.error("Adjudication API Error:", err);
      const detail = err.response?.data?.detail || "An unexpected error occurred during adjudication. Please try again.";
      setError(detail);
      setSubmitting(false);
      setSubmitStep(0);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 md:text-3xl">Adjudicate New OPD Claim</h1>
        <p className="text-sm text-slate-500 mt-1">
          Upload OPD prescriptions and receipts to trigger the automated AI parser and policy verification engine.
        </p>
      </div>

      {submitting ? (
        /* Submitting Loader UI */
        <div className="bg-white border border-slate-200 rounded-2xl p-8 md:p-12 shadow-sm flex flex-col items-center justify-center space-y-8 animate-fadeIn">
          <div className="relative flex items-center justify-center">
            <Loader2 className="h-14 w-14 text-violet-600 animate-spin" />
            <FileCheck2 className="absolute h-6 w-6 text-violet-500" />
          </div>

          <div className="text-center space-y-2">
            <h3 className="text-lg font-semibold text-slate-900">Processing Adjudication Pipeline</h3>
            <p className="text-sm text-slate-500 max-w-sm">
              Please wait. Do not close this tab. The adjudication engine is evaluating rules in real time.
            </p>
          </div>

          {/* Stepper tracker */}
          <div className="w-full max-w-md bg-slate-50 border border-slate-100 rounded-xl p-5 space-y-4">
            <div className="flex items-center gap-3">
              <div className={`h-5 w-5 rounded-full flex items-center justify-center text-xs font-semibold ${
                submitStep >= 1 ? "bg-violet-600 text-white" : "bg-slate-200 text-slate-500"
              }`}>
                {submitStep > 1 ? "✓" : "1"}
              </div>
              <span className={`text-sm ${submitStep >= 1 ? "text-slate-900 font-semibold" : "text-slate-500"}`}>
                Processing Documents & OCR text
              </span>
            </div>
            
            <div className="flex items-center gap-3">
              <div className={`h-5 w-5 rounded-full flex items-center justify-center text-xs font-semibold ${
                submitStep >= 2 ? "bg-violet-600 text-white" : "bg-slate-200 text-slate-500"
              }`}>
                {submitStep > 2 ? "✓" : "2"}
              </div>
              <span className={`text-sm ${submitStep >= 2 ? "text-slate-900 font-semibold" : "text-slate-500"}`}>
                AI Information Extraction (Gemini v2.5)
              </span>
            </div>

            <div className="flex items-center gap-3">
              <div className={`h-5 w-5 rounded-full flex items-center justify-center text-xs font-semibold ${
                submitStep >= 3 ? "bg-violet-600 text-white animate-pulse" : "bg-slate-200 text-slate-500"
              }`}>
                {submitStep > 3 ? "✓" : "3"}
              </div>
              <span className={`text-sm ${submitStep >= 3 ? "text-slate-900 font-semibold" : "text-slate-500"}`}>
                Running Claims Adjudication Rules
              </span>
            </div>
          </div>
        </div>
      ) : (
        /* Form content UI */
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
          {/* Left Column: Input Fields (col-span 7) */}
          <div className="md:col-span-7 space-y-6">
            {/* Main Form Fields Card */}
            <div className="bg-white border border-slate-200/80 rounded-xl p-5 md:p-6 shadow-sm space-y-5">
              <h2 className="text-base font-semibold text-slate-900 border-b border-slate-100 pb-3">
                Claim Information
              </h2>

              {/* Member ID Field */}
              <div className="space-y-1.5">
                <label htmlFor="memberId" className="text-xs font-semibold text-slate-600 uppercase tracking-wide flex items-center gap-1.5">
                  <User className="h-3.5 w-3.5 text-slate-400" />
                  Member ID
                </label>
                <div className="relative">
                  <input
                    type="text"
                    id="memberId"
                    value={memberId}
                    onChange={(e) => setMemberId(e.target.value)}
                    required
                    placeholder="e.g. EMP001"
                    className="w-full px-3.5 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50/50 hover:bg-slate-50/80 focus:bg-white focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/15"
                  />
                </div>
                <p className="text-xs text-slate-400">Specify active employee/member ID (EMP001 to EMP010)</p>
              </div>

              {/* Treatment Date Field */}
              <div className="space-y-1.5">
                <label htmlFor="treatmentDate" className="text-xs font-semibold text-slate-600 uppercase tracking-wide flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5 text-slate-400" />
                  Treatment Date
                </label>
                <input
                  type="date"
                  id="treatmentDate"
                  value={treatmentDate}
                  onChange={(e) => setTreatmentDate(e.target.value)}
                  required
                  className="w-full px-3.5 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50/50 focus:bg-white focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/15"
                />
              </div>

              {/* Grid: Amount + Hospital */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Claim Amount Field */}
                <div className="space-y-1.5">
                  <label htmlFor="claimAmount" className="text-xs font-semibold text-slate-600 uppercase tracking-wide flex items-center gap-1.5">
                    <DollarSign className="h-3.5 w-3.5 text-slate-400" />
                    Claim Amount (₹)
                  </label>
                  <input
                    type="number"
                    id="claimAmount"
                    min="1"
                    value={claimAmount === 0 ? "" : claimAmount}
                    onChange={(e) => setClaimAmount(Number(e.target.value))}
                    required
                    placeholder="0"
                    className="w-full px-3.5 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50/50 hover:bg-slate-50/80 focus:bg-white focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/15 font-mono"
                  />
                </div>

                {/* Hospital Name Field */}
                <div className="space-y-1.5">
                  <label htmlFor="hospitalName" className="text-xs font-semibold text-slate-600 uppercase tracking-wide flex items-center gap-1.5">
                    <Building2 className="h-3.5 w-3.5 text-slate-400" />
                    Hospital Name <span className="text-slate-400 lowercase italic">(optional)</span>
                  </label>
                  <input
                    type="text"
                    id="hospitalName"
                    value={hospitalName}
                    onChange={(e) => setHospitalName(e.target.value)}
                    placeholder="e.g. Apollo Hospital"
                    className="w-full px-3.5 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50/50 hover:bg-slate-50/80 focus:bg-white focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/15"
                  />
                </div>
              </div>
            </div>

            {/* Collapsible: Additional Parameters */}
            <div className="bg-white border border-slate-200/80 rounded-xl overflow-hidden shadow-sm">
              <button
                type="button"
                onClick={() => setShowAdditional(!showAdditional)}
                className="w-full px-5 py-4 flex items-center justify-between text-sm font-semibold text-slate-700 bg-white hover:bg-slate-50/50 active:bg-slate-50 transition-colors focus:outline-none border-none"
              >
                <span>Additional Rules Validation Parameters</span>
                {showAdditional ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </button>

              {showAdditional && (
                <div className="p-5 border-t border-slate-100 bg-slate-50/30 space-y-4 animate-fadeIn">
                  {/* Previous Claims Same Day Field */}
                  <div className="space-y-1.5">
                    <label htmlFor="prevClaims" className="text-xs font-medium text-slate-600">
                      Previous Claims Submitted on Same Day
                    </label>
                    <input
                      type="number"
                      id="prevClaims"
                      min="0"
                      value={previousClaimsSameDay}
                      onChange={(e) => setPreviousClaimsSameDay(Number(e.target.value))}
                      className="w-32 px-3 py-1.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/15"
                    />
                    <p className="text-[11px] text-slate-400">Triggers multi-submission co-pay/fraud checks if &gt; 0</p>
                  </div>

                  {/* Toggles */}
                  <div className="flex flex-col sm:flex-row gap-6 pt-2">
                    {/* Cashless Request Toggle */}
                    <label className="flex items-center gap-3 cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={cashlessRequest}
                        onChange={(e) => setCashlessRequest(e.target.checked)}
                        className="h-4.5 w-4.5 text-violet-600 border-slate-300 rounded focus:ring-violet-500/30 cursor-pointer"
                      />
                      <span className="text-xs font-medium text-slate-700">Cashless Request Pre-Authorization</span>
                    </label>

                    {/* Pre-auth Provided Toggle */}
                    <label className="flex items-center gap-3 cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={preAuthProvided}
                        onChange={(e) => setPreAuthProvided(e.target.checked)}
                        className="h-4.5 w-4.5 text-violet-600 border-slate-300 rounded focus:ring-violet-500/30 cursor-pointer"
                      />
                      <span className="text-xs font-medium text-slate-700">Pre-authorization Provided</span>
                    </label>
                  </div>
                </div>
              )}
            </div>
            
            {/* Error Message */}
            {error && (
              <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 flex items-start gap-3 text-sm animate-fadeIn">
                <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {/* Main Submit Button */}
            <button
              type="submit"
              disabled={files.length === 0 || claimAmount <= 0}
              className="w-full py-3.5 px-6 font-bold text-white bg-violet-600 hover:bg-violet-700 active:bg-violet-800 disabled:opacity-50 disabled:bg-slate-300 disabled:cursor-not-allowed rounded-xl transition-all duration-200 shadow-sm hover:shadow-md focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2"
            >
              Adjudicate Claim
            </button>
          </div>

          {/* Right Column: File Upload (col-span 5) */}
          <div className="md:col-span-5 space-y-6">
            <div className="bg-white border border-slate-200/80 rounded-xl p-5 md:p-6 shadow-sm space-y-4">
              <h2 className="text-base font-semibold text-slate-900 border-b border-slate-100 pb-3">
                Medical Documents
              </h2>

              {/* Upload Drop Zone */}
              <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={triggerFileSelect}
                className={`relative border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 ${
                  isDragActive
                    ? "border-violet-500 bg-violet-50/50 scale-[0.98]"
                    : "border-slate-300 hover:border-slate-400 hover:bg-slate-50/50"
                }`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                  multiple
                  accept="application/pdf,image/jpeg,image/png,image/webp"
                  className="hidden"
                />

                <div className={`p-3 rounded-full mb-3 transition-colors ${
                  isDragActive ? "bg-violet-100 text-violet-600" : "bg-slate-100 text-slate-500"
                }`}>
                  <Upload className="h-6 w-6" />
                </div>
                
                <p className="text-sm font-semibold text-slate-900">Drag & drop files here</p>
                <p className="text-xs text-slate-500 mt-1">or click to browse files</p>
                
                <span className="mt-4 text-[10px] uppercase font-bold tracking-wider text-slate-400 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
                  PDF, JPG, PNG, WEBP
                </span>
              </div>

              {/* Uploaded File List */}
              {files.length > 0 && (
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
                    Uploaded Files ({files.length})
                  </span>
                  
                  <div className="divide-y divide-slate-100 border border-slate-100 rounded-lg max-h-60 overflow-y-auto">
                    {files.map((file, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-slate-50/50 text-slate-700 hover:bg-slate-50 transition-colors duration-150 animate-fadeIn">
                        <div className="flex items-center gap-2.5 min-w-0 pr-2">
                          <File className="h-4 w-4 text-slate-400 shrink-0" />
                          <div className="flex flex-col min-w-0">
                            <span className="text-xs font-semibold text-slate-800 truncate" title={file.name}>
                              {file.name}
                            </span>
                            <span className="text-[10px] text-slate-400 font-mono">
                              {formatBytes(file.size)}
                            </span>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeFile(idx)}
                          className="p-1 rounded-md text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors focus:outline-none"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </form>
      )}
    </div>
  );
};

export default SubmitClaim;
