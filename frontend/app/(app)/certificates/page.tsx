import { PageHeader } from "@/components/common/page-header";
import { CertificateForm } from "@/components/certificates/certificate-form";
import { CertificateList } from "@/components/certificates/certificate-list";

export default function CertificatesPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Certificates" description="Certifications you've earned." />
      <CertificateForm />
      <CertificateList />
    </div>
  );
}
