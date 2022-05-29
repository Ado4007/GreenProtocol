use near_sdk::borsh::{self, BorshDeserialize, BorshSerialize};
use near_sdk::collections::LazyOption;
use near_sdk::collections::Vector;
use near_sdk::json_types::U128;
use near_sdk::{env, log, near_bindgen, AccountId, Balance, PanicOnDefault, PromiseOrValue};

use std::collections::HashMap;
use serde::{Serialize, Deserialize};


near_sdk::setup_alloc!();

// add the following attributes to prepare your code for serialization and invocation on the blockchain
// More built-in Rust attributes here: https://doc.rust-lang.org/reference/attributes.html#built-in-attributes-index
#[near_bindgen]
#[derive(Default, BorshDeserialize, BorshSerialize)]
pub struct GreenCertificatesEU {
    owner: AccountId, // i8 is signed. unsigned integers are also available: u8, u16, u32, u64, u128
    certificates: HashMap<AccountId, HashMap<u128, GreenCertificateEU>>
}

#[derive(BorshDeserialize, BorshSerialize, Clone, Serialize, Deserialize)]
pub struct GreenCertificateEU {
    owner: AccountId,
    amount: u128
}

#[near_bindgen]
impl GreenCertificatesEU {

    #[init]
    pub fn new() -> Self {
        // Initializing `status_updates` with unique key prefix.
        Self {
            owner: env::current_account_id(),
            certificates: HashMap::new(),
        }
    }

    #[private]
    pub fn mint_new(&mut self, receiver: AccountId, t_type: u128, amount: u128) {
        let r = receiver.clone();
        self.certificates.entry(receiver).or_insert(HashMap::new()).entry(t_type).or_insert(GreenCertificateEU{owner: r, amount: 0}).amount += amount;
    }

    pub fn get_total_balance(&self, account: AccountId) -> HashMap<u128, GreenCertificateEU> {
        match self.certificates.get(&account) {
            None => HashMap::new(),
            Some(certs) => certs.clone()
        }   
    }

    pub fn get_balance(&self, account: AccountId, t_type: u128) -> u128 {
        match self.certificates.get(&account) {
            None => 0,
            Some(certificates) => match certificates.get(&t_type) {
                None => 0,
                Some(cert) => cert.amount
            }
        }

    }

    pub fn send_tokens(&mut self, receiver: AccountId, t_types: Vec<u128>, amounts: Vec<u128>) -> String {
        if t_types.len() != amounts.len() {
            return String::from("Error");
        }
        for (t, a) in t_types.iter().zip(amounts.iter()) {
            let balance = self.get_balance(env::signer_account_id(), *t);
            if balance < *a {
                return String::from("Error: Insufficient funds");
            }
            match self.certificates.get_mut(&env::signer_account_id()) {
                None => return String::from("Error"),
                Some(certs) => {
                    match certs.get_mut(&t) {
                        None => return String::from("Error"),
                        Some(cert) => {
                            cert.amount -= a;
                            let r = receiver.clone();
                            self.certificates.entry(receiver.clone()).or_insert(HashMap::new()).entry(*t).or_insert(GreenCertificateEU{owner: r, amount: 0}).amount += a;
                        }
                    }
                }
            }
        }

        return String::from("Ok");
    }
}