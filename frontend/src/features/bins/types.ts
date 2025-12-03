/**
 * Types for the bins feature.
 */

export interface BinCollection {
  type: string;
  collection_date: string;
}

export interface BinCollectionResponse {
  address: string;
  council: string;
  bins: BinCollection[];
}

export interface BinCollectionRequest {
  postcode?: string;
  house_number?: string;
  uprn?: string;
}
