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
    "negotiation_strategy_id" TEXT,

    CONSTRAINT "debtor_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "agreement" (
    "id" TEXT NOT NULL,
    "debtor_id" TEXT NOT NULL,
    "agreement_number" TEXT NOT NULL DEFAULT '',
    "status" BOOLEAN NOT NULL DEFAULT true,
    "total_value" DECIMAL(65,30) NOT NULL,
    "original_balance" DECIMAL(65,30) NOT NULL,
    "installments" INTEGER NOT NULL,
    "total_discount" DECIMAL(65,30) NOT NULL,
    "first_payment_date" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "agreement_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "engageable_contract" (
    "id" TEXT NOT NULL,
    "debtor_id" TEXT NOT NULL,
    "status" BOOLEAN NOT NULL DEFAULT true,
    "age" INTEGER NOT NULL DEFAULT 0,
    "total_value" DECIMAL(65,30) NOT NULL,
    "original_balance" DECIMAL(65,30) NOT NULL,
    "strategy_id" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "agreement_id" TEXT,

    CONSTRAINT "engageable_contract_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "negotiation_strategy" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "negotiation_strategy_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "negotiation_rule" (
    "id" TEXT NOT NULL,
    "strategy_id" TEXT NOT NULL,
    "min_value" DECIMAL(65,30) NOT NULL,
    "max_value" DECIMAL(65,30) NOT NULL,
    "max_installments" INTEGER NOT NULL,
    "max_discount_percent" INTEGER NOT NULL,
    "min_downpayment_percent" INTEGER NOT NULL,
    "valid_until" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "negotiation_rule_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "debtor_cpf_key" ON "debtor"("cpf");

-- CreateIndex
CREATE UNIQUE INDEX "engageable_contract_agreement_id_key" ON "engageable_contract"("agreement_id");

-- CreateIndex
CREATE UNIQUE INDEX "negotiation_strategy_name_key" ON "negotiation_strategy"("name");

-- AddForeignKey
ALTER TABLE "debtor" ADD CONSTRAINT "debtor_negotiation_strategy_id_fkey" FOREIGN KEY ("negotiation_strategy_id") REFERENCES "negotiation_strategy"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "agreement" ADD CONSTRAINT "agreement_debtor_id_fkey" FOREIGN KEY ("debtor_id") REFERENCES "debtor"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "engageable_contract" ADD CONSTRAINT "engageable_contract_debtor_id_fkey" FOREIGN KEY ("debtor_id") REFERENCES "debtor"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "engageable_contract" ADD CONSTRAINT "engageable_contract_strategy_id_fkey" FOREIGN KEY ("strategy_id") REFERENCES "negotiation_strategy"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "engageable_contract" ADD CONSTRAINT "engageable_contract_agreement_id_fkey" FOREIGN KEY ("agreement_id") REFERENCES "agreement"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "negotiation_rule" ADD CONSTRAINT "negotiation_rule_strategy_id_fkey" FOREIGN KEY ("strategy_id") REFERENCES "negotiation_strategy"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
