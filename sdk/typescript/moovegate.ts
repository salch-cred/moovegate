/**
 * MooveGate TypeScript / Node.js SDK
 * Type-safe client and middleware for Moove Agentic Payments.
 */

export interface PaymentLinkCreateOptions {
  toAmount: string; // Decimal string e.g. "19.99"
  description?: string;
  maxUsage?: number;
  expirationDate?: string | null;
}

export interface PaymentLink {
  id: string;
  url: string;
  status: 'active' | 'completed' | 'inactive';
  toAmount: string;
  receivedAmount?: string | null;
  description?: string;
  createdAt?: string;
}

export interface PaywallChallenge {
  statusCode: 402;
  error: string;
  paymentLinkId: string;
  paymentUrl: string;
  amountUsdc: string;
  referenceId: string;
}

export class MooveClient {
  private apiKey: string;
  private baseUrl: string;
  public sandbox: boolean;
  private mockDb: Map<string, PaymentLink> = new Map();

  constructor(options?: { apiKey?: string; baseUrl?: string; sandbox?: boolean }) {
    this.apiKey = options?.apiKey || process.env.MOOVE_API_KEY || '';
    this.baseUrl = (options?.baseUrl || process.env.MOOVE_API_BASE_URL || 'https://api.moove.xyz').replace(/\/$/, '');
    this.sandbox = options?.sandbox ?? (!this.apiKey || this.apiKey.includes('mock') || this.apiKey.includes('test'));
  }

  private getHeaders(): Record<string, string> {
    if (!this.apiKey && !this.sandbox) {
      throw new Error('MOOVE_API_KEY environment variable is not configured.');
    }
    return {
      'X-API-Key': this.apiKey || 'mk_sandbox_dummy',
      'Content-Type': 'application/json',
      'User-Agent': 'MooveGate-TypeScript/1.0.0',
    };
  }

  async createPaymentLink(options: PaymentLinkCreateOptions): Promise<PaymentLink> {
    if (this.sandbox) {
      const linkId = `pl_mock_${Math.random().toString(36).substring(2, 14)}`;
      const link: PaymentLink = {
        id: linkId,
        url: `https://pay.moove.xyz/link/${linkId}`,
        status: 'active',
        toAmount: options.toAmount,
        receivedAmount: null,
        description: options.description,
        createdAt: new Date().toISOString(),
      };
      this.mockDb.set(linkId, link);
      return link;
    }

    const res = await fetch(`${this.baseUrl}/v1/payment-link`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(options),
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`Moove API Error (${res.status}): ${err}`);
    }

    return (await res.json()) as PaymentLink;
  }

  async getPaymentLink(linkId: string): Promise<PaymentLink> {
    if (this.sandbox) {
      const link = this.mockDb.get(linkId);
      if (!link) throw new Error(`Link ${linkId} not found in sandbox.`);
      return link;
    }

    const res = await fetch(`${this.baseUrl}/v1/payment-link/${linkId}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!res.ok) {
      throw new Error(`Failed to fetch Moove link ${linkId}`);
    }

    return (await res.json()) as PaymentLink;
  }

  async simulatePayment(linkId: string): Promise<PaymentLink> {
    if (!this.sandbox) throw new Error('Simulation only available in sandbox mode.');
    const link = this.mockDb.get(linkId);
    if (!link) throw new Error(`Link ${linkId} not found.`);
    link.status = 'completed';
    link.receivedAmount = link.toAmount;
    return link;
  }
}
