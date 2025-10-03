-- CreateTable
CREATE TABLE "debtor" (
    "id" TEXT NOT NULL,
    "cpf" TEXT NOT NULL,
    "phone" TEXT,
    "email" TEXT,
    "full_name" TEXT,
    "birth_date" TEXT,
    "mother_name" TEXT,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "authorized" BOOLEAN NOT NULL DEFAULT false,
    "trust_level" INTEGER NOT NULL DEFAULT 0,
    "score" INTEGER NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "debtor_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "access_log" (
    "id" TEXT NOT NULL,
    "debtor_id" TEXT NOT NULL,
    "token" TEXT,
    "ip_address" TEXT,
    "device_id" TEXT,
    "finished_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "utm_id" TEXT,
    "utm_campaign" TEXT,
    "utm_source" TEXT,
    "utm_medium" TEXT,
    "utm_content" TEXT,
    "utm_term" TEXT,

    CONSTRAINT "access_log_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sms_token" (
    "id" TEXT NOT NULL,
    "debtor_id" TEXT NOT NULL,
    "token" TEXT,
    "phone" TEXT,
    "subject" TEXT,
    "message" TEXT,
    "message_id" TEXT,
    "expires_at" TIMESTAMP(3) NOT NULL DEFAULT (now() + '01:00:00'::interval),
    "active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "sms_token_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "enrichment" (
    "id" TEXT NOT NULL,
    "debtor_id" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "result" TEXT NOT NULL,
    "summary" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "enrichment_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "profile" (
    "id" TEXT NOT NULL,
    "debtor_id" TEXT NOT NULL,
    "phone" TEXT,
    "email" TEXT,
    "locale" TEXT,
    "number" TEXT,
    "complement" TEXT,
    "region" TEXT,
    "city" TEXT,
    "postal_code" TEXT,
    "state" TEXT,
    "pending" BOOLEAN NOT NULL DEFAULT true,
    "active" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "profile_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "exception" (
    "id" TEXT NOT NULL,
    "access_log_id" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "cpf" TEXT NOT NULL,
    "full_name" TEXT,
    "birth_date" TEXT,
    "phone" TEXT,
    "email" TEXT,
    "cpf_attempt" TEXT,
    "full_name_attempt" TEXT,
    "birth_date_attempt" TEXT,
    "phone_attempt" TEXT,
    "email_attempt" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "exception_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "agreement" (
    "id" TEXT NOT NULL,
    "debtor_id" TEXT NOT NULL,
    "contract" TEXT NOT NULL,
    "error" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "agreement_number" TEXT NOT NULL DEFAULT '',
    "status" BOOLEAN NOT NULL DEFAULT false,
    "total_discount" DECIMAL(65,30),

    CONSTRAINT "agreement_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "proposal" (
    "id" TEXT NOT NULL,
    "status" BOOLEAN NOT NULL DEFAULT true,
    "agreement_id" TEXT NOT NULL,
    "total_installments" INTEGER NOT NULL,
    "total_value" DECIMAL(65,30) NOT NULL,
    "installment_value" DECIMAL(65,30) NOT NULL,
    "total_discount" DECIMAL(65,30),
    "original_balance" DECIMAL(65,30) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "proposal_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "debtor_cpf_key" ON "debtor"("cpf");

-- AddForeignKey
ALTER TABLE "access_log" ADD CONSTRAINT "access_log_debtor_id_fkey" FOREIGN KEY ("debtor_id") REFERENCES "debtor"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sms_token" ADD CONSTRAINT "sms_token_debtor_id_fkey" FOREIGN KEY ("debtor_id") REFERENCES "debtor"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "enrichment" ADD CONSTRAINT "enrichment_debtor_id_fkey" FOREIGN KEY ("debtor_id") REFERENCES "debtor"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "profile" ADD CONSTRAINT "profile_debtor_id_fkey" FOREIGN KEY ("debtor_id") REFERENCES "debtor"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "exception" ADD CONSTRAINT "exception_access_log_id_fkey" FOREIGN KEY ("access_log_id") REFERENCES "access_log"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "agreement" ADD CONSTRAINT "agreement_debtor_id_fkey" FOREIGN KEY ("debtor_id") REFERENCES "debtor"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "proposal" ADD CONSTRAINT "proposal_agreement_id_fkey" FOREIGN KEY ("agreement_id") REFERENCES "agreement"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
