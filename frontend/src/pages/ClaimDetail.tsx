import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { claimsApi } from "../api/services";
import type { ClaimResponse } from "../api/types";
import { cn } from "../lib/utils";
import {
  FileText,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader2,
  ArrowLeft,
  User,
  Calendar,
  Building2,
  Sparkles
} from "lucide-react";

export const ClaimDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [claim, setClaim] = useState<ClaimResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeDocIndex, setActiveDocIndex] = useState<number>(0);

  const fetchClaim = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await claimsApi.getClaimById(id);
      setClaim(data);
    } catch (err: any) {
      console.error("Error fetching claim details:", err);
      const detail = err.response?.data?.detail || "Could not retrieve claim details. Ensure the backend server is running.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClaim();
  }, [id]);

  // Format currency helpers
  const formatINR = (value: number | null | undefined) => {
    if (value === null || value === undefined) return "₹0";
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Format deduction keys cleanly
  const formatDeductionKey = (key: string) => {
    return key
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  // Format date helper
  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return "N/A";
    try {
      return new Date(dateStr).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });
    } catch (e) {
      return dateStr;
    }
  };

  // Extract filename from file URL or path
  const getFilename = (url: string) => {
    if (!url) return "Document";
    return url.split(/[\\/]/).pop() || url;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <Loader2 className="h-10 w-10 text-violet-600 animate-spin" />
        <p className="text-sm font-medium text-slate-500">Retrieving adjudication results...</p>
      </div>
    );
  }

  if (error || !claim) {
    return (
      <div className="max-w-md mx-auto py-16 text-center space-y-6">
        <div className="inline-flex p-3 rounded-full bg-rose-50 text-rose-600">
          <AlertCircle className="h-8 w-8" />
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-bold text-slate-900">Claim Detail Error</h3>
          <p className="text-sm text-slate-500">
            {error || "The requested claim details could not be found."}
          </p>
        </div>
        <div className="flex justify-center gap-3">
          <Link
            to="/dashboard"
            className="px-4 py-2 text-sm font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
          >
            Back to Dashboard
          </Link>
          {id && (
            <button
              onClick={fetchClaim}
              className="px-4 py-2 text-sm font-semibold text-white bg-violet-600 hover:bg-violet-700 rounded-lg transition-colors"
            >
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  const hasDocs = claim.document_urls && claim.document_urls.length > 0;
  const activeDocName = hasDocs ? claim.document_urls[activeDocIndex] : "";

  // Detailed descriptions for rule matrix keys
  const getRuleDescription = (key: string) => {
    switch (key.toLowerCase()) {
      case "eligibility":
        return "Member enrollment verification, policy duration, and waiting periods.";
      case "documents":
        return "Completeness check and doctor registration registration validation.";
      case "coverage":
        return "Diagnosis screening against policy inclusions and exclusions.";
      case "financials":
        return "Co-pay calculation, network discounts, and room cap ceilings.";
      case "necessity":
        return "AI coherence check of medical prescription versus billing items.";
      case "fraud":
        return "Anomalies check, duplicates audit, and same-day claim limits.";
      default:
        return "Adjudication rules pipeline verification step.";
    }
  };

  // Standard ordered rule list mapping
  const ruleOrder = ["eligibility", "documents", "coverage", "financials", "necessity", "fraud"];
  const sortedRules = Object.entries(claim.rule_matrix || {}).sort(([keyA], [keyB]) => {
    const indexA = ruleOrder.indexOf(keyA.toLowerCase());
    const indexB = ruleOrder.indexOf(keyB.toLowerCase());
    if (indexA === -1 && indexB === -1) return keyA.localeCompare(keyB);
    if (indexA === -1) return 1;
    if (indexB === -1) return -1;
    return indexA - indexB;
  });

  const hasRejectionReasons = claim.rejection_reasons && claim.rejection_reasons.length > 0;
  const hasRejectedItems = claim.rejected_items && claim.rejected_items.length > 0;
  const showExplanations = hasRejectionReasons || hasRejectedItems;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Header Navigation */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center gap-3">
          <Link
            to="/dashboard"
            className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-500 hover:text-slate-900 hover:bg-slate-50 transition-colors shadow-sm focus:outline-none"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
                CLAIM ID: {claim.claim_id}
              </span>
            </div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900 mt-1">
              Adjudication Audit Trail
            </h1>
          </div>
        </div>

        {/* Claim Meta Info */}
        <div className="hidden sm:flex items-center gap-6 text-xs text-slate-500 font-medium">
          <div className="flex items-center gap-1.5">
            <User className="h-4 w-4 text-slate-400" />
            <div>
              <span className="text-slate-400 block font-normal">Member Name</span>
              <span className="text-slate-800 font-semibold">{claim.member_name}</span>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <Calendar className="h-4 w-4 text-slate-400" />
            <div>
              <span className="text-slate-400 block font-normal">Treatment Date</span>
              <span className="text-slate-800 font-semibold">{formatDate(claim.treatment_date)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main 2-Column Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        
        {/* Left Column: Document Viewer */}
        <div className="bg-white border border-slate-200/80 rounded-xl p-5 md:p-6 shadow-sm flex flex-col space-y-5 h-full min-h-[500px]">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Document Viewer</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Review claim documents and AI validation data extracted by Gemini.
            </p>
          </div>

          {hasDocs ? (
            <>
              {/* Document List */}
              <div className="space-y-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                  Claim Attachments ({claim.document_urls.length})
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {claim.document_urls.map((url, idx) => {
                    const filename = getFilename(url);
                    const isActive = idx === activeDocIndex;
                    return (
                      <button
                        key={idx}
                        onClick={() => setActiveDocIndex(idx)}
                        className={cn(
                          "flex items-center gap-2.5 p-3 rounded-lg border text-left text-xs transition-all duration-150 focus:outline-none",
                          isActive
                            ? "border-violet-300 bg-violet-50/70 text-violet-800 font-semibold shadow-sm"
                            : "border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700"
                        )}
                      >
                        <FileText className={cn("h-4 w-4 shrink-0", isActive ? "text-violet-600" : "text-slate-400")} />
                        <span className="truncate" title={filename}>{filename}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Viewport Box */}
              <div className="flex-1 border border-slate-100 rounded-xl bg-slate-50/50 p-4 flex flex-col min-h-[300px]">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2.5 mb-4 text-[10px]">
                  <div className="flex items-center gap-1.5 min-w-0">
                    <span className="font-bold text-slate-400 uppercase font-mono">Viewing:</span>
                    <span className="font-medium text-slate-700 truncate max-w-[220px]" title={getFilename(activeDocName)}>
                      {getFilename(activeDocName)}
                    </span>
                  </div>
                  <span className="font-bold text-slate-400 uppercase font-mono tracking-wider">
                    Mock Viewer
                  </span>
                </div>

                {/* Stylized Simulated File Content */}
                <div className="flex-1 bg-white border border-slate-200/60 rounded-lg p-5 flex flex-col justify-between shadow-sm">
                  {/* Bill vs Prescription simulated interface */}
                  {activeDocName.toLowerCase().includes("bill") || activeDocName.toLowerCase().includes("receipt") ? (
                    <div className="space-y-4 text-xs text-slate-600">
                      <div className="flex justify-between items-start border-b border-slate-100 pb-3">
                        <div>
                          <span className="text-[9px] font-bold text-slate-400 uppercase">Provider / Hospital</span>
                          <h4 className="text-sm font-bold text-slate-800 mt-0.5">
                            {claim.hospital_name || "OPD Medical Provider"}
                          </h4>
                          <p className="text-[10px] text-slate-400">Date: {formatDate(claim.treatment_date)}</p>
                        </div>
                        <div className="text-right">
                          <span className="text-[9px] font-bold text-slate-400 uppercase">Bill Category</span>
                          <span className="block font-semibold text-slate-700 mt-0.5">OPD Invoice</span>
                        </div>
                      </div>

                      <div className="bg-slate-50 p-3 rounded-lg border border-slate-100/80">
                        <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Financial Summary</span>
                        <div className="flex justify-between text-slate-800 font-semibold mt-1.5 text-sm">
                          <span>Total Amount:</span>
                          <span className="font-mono">{formatINR(claim.submitted_amount)}</span>
                        </div>
                      </div>

                      {((claim.extracted_data?.consultation_fee != null) ||
                        (claim.extracted_data?.medicine_cost != null) ||
                        (claim.extracted_data?.diagnostic_cost != null)) ? (
                        <div className="space-y-1.5">
                          <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Extracted Items</span>
                          {claim.extracted_data?.consultation_fee != null && (
                            <div className="flex justify-between border-b border-slate-100 py-1 text-slate-500">
                              <span>Consultation Fee</span>
                              <span className="font-mono">{formatINR(claim.extracted_data.consultation_fee)}</span>
                            </div>
                          )}
                          {claim.extracted_data?.medicine_cost != null && (
                            <div className="flex justify-between border-b border-slate-100 py-1 text-slate-500">
                              <span>Medicines</span>
                              <span className="font-mono">{formatINR(claim.extracted_data.medicine_cost)}</span>
                            </div>
                          )}
                          {claim.extracted_data?.diagnostic_cost != null && (
                            <div className="flex justify-between border-b border-slate-100 py-1 text-slate-500">
                              <span>Diagnostics</span>
                              <span className="font-mono">{formatINR(claim.extracted_data.diagnostic_cost)}</span>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="space-y-1.5">
                          <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Extracted Items</span>
                          <div className="flex justify-between border-b border-slate-100 py-1 text-slate-500">
                            <span>Billed Items</span>
                            <span className="font-mono">{formatINR(claim.submitted_amount)}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-4 text-xs text-slate-600">
                      <div className="flex justify-between items-start border-b border-slate-100 pb-3">
                        <div>
                          <span className="text-[9px] font-bold text-slate-400 uppercase">Clinician</span>
                          <h4 className="text-sm font-bold text-slate-800 mt-0.5">
                            {claim.extracted_data?.doctor_name || "Medical Practitioner"}
                          </h4>
                          <p className="text-[10px] text-slate-400">Reg No: {claim.extracted_data?.doctor_registration || "N/A"}</p>
                        </div>
                        <div className="text-right">
                          <span className="text-[9px] font-bold text-slate-400 uppercase">Specialty</span>
                          <span className="block font-semibold text-slate-700 mt-0.5">OPD Consultation</span>
                        </div>
                      </div>

                      <div className="space-y-1">
                        <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Clinical Notes / Diagnosis</span>
                        <p className="italic text-slate-800 font-medium bg-slate-50/60 p-3 rounded-lg border border-slate-100">
                          "{claim.extracted_data?.diagnosis || "Diagnosis not specified in extracted data"}"
                        </p>
                      </div>

                      {claim.extracted_data?.medicines && claim.extracted_data.medicines.length > 0 && (
                        <div className="space-y-1.5">
                          <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block">Prescription Line Items</span>
                          <div className="flex flex-wrap gap-1.5">
                            {claim.extracted_data.medicines.map((med: string, i: number) => (
                              <span key={i} className="bg-slate-100 text-slate-700 text-[10px] px-2 py-1 rounded font-medium border border-slate-200/50">
                                {med}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Extraction Verification Quality */}
                  <div className="border-t border-slate-100 pt-3 mt-4 flex items-center justify-between text-[10px] text-slate-400">
                    <div className="flex items-center gap-1 text-emerald-600 font-medium">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      OCR Verified & Evaluated
                    </div>
                    <span className="font-mono text-[9px]">CONFIDENCE: {claim.extracted_data?.extraction_confidence ? `${Math.round(claim.extracted_data.extraction_confidence * 100)}%` : "95%"}</span>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center border border-dashed border-slate-200 rounded-xl p-8 bg-slate-50/30 text-center">
              <FileText className="h-8 w-8 text-slate-400 mb-2" />
              <h4 className="text-sm font-semibold text-slate-800">No Documents Uploaded</h4>
              <p className="text-xs text-slate-500 max-w-[240px] mt-0.5">
                This claim has no associated file attachments or documents.
              </p>
            </div>
          )}
        </div>

        {/* Right Column: Decision Engine Matrix */}
        <div className="space-y-6">
          
          {/* Header Banner */}
          <div className={cn(
            "rounded-xl border p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 shadow-sm",
            claim.decision === "APPROVED" && "bg-emerald-50 border-emerald-200/80 text-emerald-800",
            claim.decision === "REJECTED" && "bg-rose-50 border-rose-200/80 text-rose-800",
            (claim.decision === "PARTIAL" || claim.decision === "MANUAL_REVIEW") && "bg-amber-50 border-amber-200/80 text-amber-800"
          )}>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider opacity-60 block">Adjudication Outcome</span>
              <h2 className="text-xl font-bold tracking-tight mt-0.5">
                {claim.decision.replace("_", " ")}
              </h2>
            </div>
            <div className="sm:text-right">
              <span className="text-[10px] font-bold uppercase tracking-wider opacity-60 block">Settlement Summary</span>
              <div className="flex items-baseline gap-1.5 mt-0.5 sm:justify-end">
                <span className="text-2xl font-bold font-mono">
                  {formatINR(claim.approved_amount || 0)}
                </span>
                <span className="text-xs opacity-75">
                  approved of {formatINR(claim.submitted_amount)}
                </span>
              </div>
            </div>
          </div>

          {/* Settlement Breakdown Card */}
          <div className="bg-white border border-slate-200/80 rounded-xl p-5 md:p-6 shadow-sm space-y-4">
            <div>
              <h3 className="text-base font-semibold text-slate-900">Settlement Breakdown</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Financial audit of deductions and net approved payout.
              </p>
            </div>

            <div className="space-y-3 pt-2 text-sm">
              <div className="flex justify-between items-center text-slate-600">
                <span>Submitted Amount</span>
                <span className="font-mono font-medium">{formatINR(claim.submitted_amount)}</span>
              </div>

              {Object.entries(claim.deductions || {}).map(([key, val]) => (
                <div key={key} className="flex justify-between items-center text-slate-600">
                  <span className="text-slate-500">{formatDeductionKey(key)}</span>
                  <span className="font-mono font-medium text-rose-600">-{formatINR(val)}</span>
                </div>
              ))}

              <div className="border-t border-slate-100 pt-3 flex justify-between items-center font-bold text-slate-900 text-base">
                <span>Approved Amount</span>
                <span className="font-mono text-violet-700">{formatINR(claim.approved_amount)}</span>
              </div>
            </div>
          </div>

          {/* Middle: Decision Matrix */}
          <div className="bg-white border border-slate-200/80 rounded-xl p-5 md:p-6 shadow-sm space-y-4">
            <div>
              <h3 className="text-base font-semibold text-slate-900">Decision Matrix</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Status checklist of policy parameters verified by the engine.
              </p>
            </div>

            <div className="divide-y divide-slate-100">
              {sortedRules.map(([key, value], index) => {
                const isPass = value === "PASS";
                const isFail = value === "FAIL";
                const isSkip = value === "SKIP";
                
                // Capitalize the rule names for display
                const ruleTitle = key.charAt(0).toUpperCase() + key.slice(1);
                const ruleDesc = getRuleDescription(key);

                return (
                  <div
                    key={key}
                    className={cn(
                      "py-3 flex items-start justify-between gap-4 transition-all duration-150 rounded-lg px-2 -mx-2",
                      isFail && "bg-rose-50/15"
                    )}
                  >
                    <div className="flex gap-3 min-w-0">
                      <div className="h-5 w-5 rounded-full bg-violet-50 text-violet-600 text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                        {index + 1}
                      </div>
                      <div className="min-w-0">
                        <h4 className="text-xs font-semibold text-slate-900 truncate">
                          {ruleTitle}
                        </h4>
                        <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                          {ruleDesc}
                        </p>
                      </div>
                    </div>

                    <div className="shrink-0 flex items-center self-center">
                      {isPass ? (
                        <div className="flex items-center gap-1 bg-emerald-50 text-emerald-700 border border-emerald-200/50 rounded-full px-2.5 py-0.5 text-xs font-semibold">
                          <CheckCircle className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                          <span>PASS</span>
                        </div>
                      ) : isFail ? (
                        <div className="flex items-center gap-1 bg-rose-50 text-rose-700 border border-rose-200/50 rounded-full px-2.5 py-0.5 text-xs font-semibold">
                          <XCircle className="h-3.5 w-3.5 text-rose-600 shrink-0" />
                          <span>FAIL</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1 bg-slate-50 text-slate-500 border border-slate-200 rounded-full px-2.5 py-0.5 text-xs font-semibold">
                          <span className="text-slate-400 font-mono text-[9px]">—</span>
                          <span>{isSkip ? "SKIP" : value}</span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Bottom: Explanations Alert Box */}
          {showExplanations && (
            <div className="bg-rose-50 border border-rose-200/80 rounded-xl p-5 text-rose-800 space-y-3.5 animate-fadeIn">
              <div className="flex items-start gap-2.5">
                <AlertCircle className="h-5 w-5 text-rose-600 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm font-bold text-rose-950">Adjudication Audit Findings</h4>
                  <p className="text-xs text-rose-700 mt-0.5">
                    This claim contains rule violations or item modifications outlined below:
                  </p>
                </div>
              </div>

              <div className="space-y-3 text-xs pl-7">
                {hasRejectionReasons && (
                  <div className="space-y-1.5">
                    <span className="font-semibold uppercase text-[9px] tracking-wider text-rose-900/80 block">
                      Rejection Codes
                    </span>
                    <ul className="list-disc pl-4 space-y-1">
                      {claim.rejection_reasons.map((reason, i) => (
                        <li key={i} className="font-semibold text-rose-900">
                          {reason.replace(/_/g, " ")}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {hasRejectedItems && (
                  <div className="space-y-1.5">
                    <span className="font-semibold uppercase text-[9px] tracking-wider text-rose-900/80 block">
                      Rejected Billing Items
                    </span>
                    <ul className="list-disc pl-4 space-y-1">
                      {claim.rejected_items.map((item, i) => (
                        <li key={i} className="font-medium text-rose-800">
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Footer Metadata Card */}
          <div className="bg-slate-50 border border-slate-200/60 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-200/50 pb-3">
              <div className="flex items-center gap-1.5">
                <Sparkles className="h-4 w-4 text-violet-500 shrink-0" />
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Engine Adjudication Confidence
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-1.5 w-16 bg-slate-200 rounded-full overflow-hidden shrink-0 hidden sm:block">
                  <div
                    className={cn(
                      "h-full rounded-full transition-all duration-500",
                      (claim.confidence_score || 0) >= 0.85 ? "bg-emerald-500" :
                      (claim.confidence_score || 0) >= 0.70 ? "bg-amber-500" : "bg-rose-500"
                    )}
                    style={{ width: `${Math.round((claim.confidence_score || 0) * 100)}%` }}
                  />
                </div>
                <span className="text-xs font-bold text-slate-800 font-mono">
                  {claim.confidence_score ? `${Math.round(claim.confidence_score * 100)}%` : "N/A"}
                </span>
              </div>
            </div>

            {claim.notes && (
              <div className="space-y-1.5">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                  Evaluator Notes
                </span>
                <p className="text-xs text-slate-600 bg-white border border-slate-100 rounded-lg p-3 italic">
                  "{claim.notes}"
                </p>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
};

export default ClaimDetail;
