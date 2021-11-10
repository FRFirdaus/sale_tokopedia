all_orders_dummy = {
    "header": {
        "process_time": 0.018328845,
        "messages": "Your request has been processed successfully"
    },
    "data": [
        {
            "fs_id": "15494",
            "order_id": 12345678,
            "is_cod_mitra": False,
            "accept_partial": False,
            "invoice_ref_num": "INV/20200110/XX/I/502",
            "products": [
                {
                    "id": 15242279,
                    "name": "Chitato Rasa Beef BBQ 35 gr isi 20 pcs",
                    "quantity": 1,
                    "notes": "",
                    "weight": 0.004,
                    "total_weight": 0.004,
                    "price": 98784,
                    "total_price": 98784,
                    "currency": "Rp",
                    "sku": "11550001",
                    "is_wholesale" : True
                }
            ],
            "products_fulfilled": [
                {
                    "product_id": 15242279,
                    "quantity_deliver": 1,
                    "quantity_reject": 0
                }
            ],
            "device_type": "",
            "buyer": {
                "id": 8970588,
                "name": "Mitra Test Account",
                "phone": "62888888888",
                "email": "mitra_test@tokopedia.com"
            },
            "shop_id": 12180715,
            "payment_id": 11687315,
            "recipient": {
                "name": "Mitra Test Account",
                "phone": "62888888888",
                "address": {
                    "address_full": "Kobakma, Kab. Mamberamo Tengah, Papua, 99558",
                    "district": "Kobakma",
                    "city": "Kab. Mamberamo Tengah",
                    "province": "Papua",
                    "country": "Indonesia",
                    "postal_code": "99558",
                    "district_id": 5455,
                    "city_id": 555,
                    "province_id": 33,
                    "geo": "-3.69624360109313,139.10973580486393"
                }
            },
            "logistics": {
                "shipping_id": 999,
                "district_id": 0,
                "city_id": 0,
                "province_id": 0,
                "geo": "",
                "shipping_agency": "Custom Logistik",
                "service_type": "Service Normal"
            },
            "amt": {
                "ttl_product_price": 98784,
                "shipping_cost": 10000,
                "insurance_cost": 0,
                "ttl_amount": 108784,
                "voucher_amount": 0,
                "toppoints_amount": 0
            },
            "dropshipper_info": {},
            "voucher_info": {
                "voucher_code": "",
                "voucher_type": 0
            },
            "order_status": 700,
            "warehouse_id": 0,
            "fulfill_by": 0,
            "create_time": 1578671153,
            "custom_fields": {
                "awb": "CSDRRRRR502"
            },
            "promo_order_detail": {
                "order_id": 43481289,
                "total_cashback": 0,
                "total_discount": 20000,
                "total_discount_product": 10000,
                "total_discount_shipping": 10000,
                "total_discount_details":[
                    {
                      "amount":10000,
                      "type":"discount_product"
                    },
                    {
                      "amount":10000,
                      "type":"discount_shipping"
                    }
                ],
                "summary_promo": [
                    {
                        "name": "Promo Product July",
                        "is_coupon": False,
                        "show_cashback_amount": True,
                        "show_discount_amount": True,
                        "cashback_amount": 0,
                        "cashback_points": 0,
                        "type": "discount",
                        "discount_amount": 10000,
                        "discount_details": [
                          {
                             "amount" : 10000,
                             "type"   : "discount_product"
                          }
                         ],
                        "invoice_desc": "PRODUCTDISC"
                    },
                    {
                        "name": "Promo Ongkir",
                        "is_coupon": False,
                        "show_cashback_amount": True,
                        "show_discount_amount": True,
                        "cashback_amount": 0,
                        "cashback_points": 0,
                        "type": "discount",
                        "discount_amount": 10000,
                        "discount_details": [
                           {
                             "amount" : 10000,
                             "type"   : "discount_shipping"
                           }
                         ],
                        "invoice_desc": "ONGKIRFREE"
                    }
                ]
            }
        }
    ]
}

single_order_dummy = {
    "header": {
        "process_time": 0.149503274,
        "messages": "Your request has been processed successfully"
    },
    "data": {
        "order_id": 12345678,
        "buyer_id": 5511917,
        "seller_id": 12180715,
        "payment_id": 11539459,
        "is_affiliate": False,
        "is_fulfillment": False,
        "order_warehouse": {
            "warehouse_id": 0,
            "fulfill_by": 0,
            "meta_data": {
                "warehouse_id": 0,
                "partner_id": 0,
                "shop_id": 0,
                "warehouse_name": "",
                "district_id": 0,
                "district_name": "",
                "city_id": 0,
                "city_name": "",
                "province_id": 0,
                "province_name": "",
                "status": 0,
                "postal_code": "",
                "is_default": 0,
                "latlon": "",
                "latitude": "",
                "longitude": "",
                "email": "",
                "address_detail": "",
                "country_name": "",
                "is_fulfillment": False
            }
        },
        "order_status": 0,
        "invoice_number": "INV/20170720/XVII/VII/12472252",
        "invoice_pdf": "Invoice-5511917-479573-20170720175058-WE1NWElRVVk.pdf",
        "invoice_url": "https://staging.tokopedia.com/invoice.pl?id=12472302&pdf=Invoice-5511917-479573-20170720175058-WE1NWElRVVk",
        "open_amt": 270000,
        "lp_amt": 0,
        "cashback_amt": 0,
        "info": "",
        "comment": "* 24/07/2017 08:01:07 : Penjual telah melebihi batas waktu proses pesanan",
        "item_price": 261000,
        "buyer_info": {
            "buyer_id": 5511917,
            "buyer_fullname": "Maulana Hasim",
            "buyer_email": "maulana.hasim@tokopedia.com",
            "buyer_phone": "6287774160644"
        },
        "shop_info": {
            "shop_owner_id": 5510391,
            "shop_owner_email": "hana.mahrifah+inti@tokopedia.com",
            "shop_owner_phone": "628119916444",
            "shop_name": "I`nti.Cosmetic",
            "shop_domain": "icl",
            "shop_id": 479573
        },
        "shipment_fulfillment": {
            "id": 0,
            "order_id": 0,
            "payment_date_time": "0001-01-01T00:00:00Z",
            "is_same_day": False,
            "accept_deadline": "0001-01-01T00:00:00Z",
            "confirm_shipping_deadline": "0001-01-01T00:00:00Z",
            "item_delivered_deadline": {
                "Time": "0001-01-01T00:00:00Z",
                "Valid": False
            },
            "is_accepted": False,
            "is_confirm_shipping": False,
            "is_item_delivered": False,
            "fulfillment_status": 0
        },
        "preorder": {
            "order_id": 0,
            "preorder_type": 0,
            "preorder_process_time": 0,
            "preorder_process_start": "2017-07-20T17:50:58.061156Z",
            "preorder_deadline": "0001-01-01T00:00:00Z",
            "shop_id": 0,
            "customer_id": 0
        },
        "order_info": {
            "order_detail": [
                {
                    "order_detail_id": 20274955,
                    "product_id": 14286600,
                    "product_name": "STABILO Paket Ballpoint Premium Bionic Rollerball - Multicolor",
                    "product_desc_pdp": "Paket\n pulpen premium membuat kegiatan menulis kamu bisa lebih berwarna kenyamanan yang maksimal- memiliki 4 warna Paket\n pulpen premium membuat kegiatan menulis kamu bisa lebih berwarna kenyamanan yang maksimal- memiliki 4 warna",
                    "product_desc_atc": "Paket\n pulpen premium membuat kegiatan menulis kamu bisa lebih berwarna kenyamanan yang maksimal- memiliki 4 warna Paket\n pulpen premium membuat kegiatan menulis kamu bisa lebih berwarna kenyamanan yang maksimal- memiliki 4 warna",
                    "product_price": 261000,
                    "subtotal_price": 261000,
                    "weight": 0.2,
                    "total_weight": 0.2,
                    "quantity": 1,
                    "quantity_deliver": 1,
                    "quantity_reject": 0,
                    "is_free_returns": False,
                    "insurance_price": 0,
                    "normal_price": 0,
                    "currency_id": 2,
                    "currency_rate": 0,
                    "min_order": 0,
                    "child_cat_id": 1122,
                    "campaign_id": "",
                    "product_picture": "https://imagerouter-staging.tokopedia.com/image/v1/p/14286600/product_detail/desktop",
                    "snapshot_url": "https://staging.tokopedia.com/snapshot_product?order_id=12472302&dtl_id=20274955",
                    "sku": "SKU01"
                }
            ],
            "order_history": [
                {
                    "action_by": "system-automatic",
                    "hist_status_code": 0,
                    "message": "",
                    "timestamp": "2017-07-24T08:01:07.073696Z",
                    "comment": "Penjual telah melebihi batas waktu proses pesanan",
                    "create_by": 0,
                    "update_by": "system"
                },
                {
                    "action_by": "buyer",
                    "hist_status_code": 220,
                    "message": "",
                    "timestamp": "2017-07-20T17:50:58.374626Z",
                    "comment": "",
                    "create_by": 0,
                    "update_by": "tokopedia"
                },
                {
                    "action_by": "buyer",
                    "hist_status_code": 100,
                    "message": "",
                    "timestamp": "2017-07-20T17:50:58.374626Z",
                    "comment": "",
                    "create_by": 0,
                    "update_by": "system"
                }
            ],
            "order_age_day": 812,
            "shipping_age_day": 0,
            "delivered_age_day": 0,
            "partial_process": False,
            "shipping_info": {
                "sp_id": 1,
                "shipping_id": 1,
                "logistic_name": "JNE",
                "logistic_service": "Reguler",
                "shipping_price": 9000,
                "shipping_price_rate": 9000,
                "shipping_fee": 0,
                "insurance_price": 0,
                "fee": 0,
                "is_change_courier": False,
                "second_sp_id": 0,
                "second_shipping_id": 0,
                "second_logistic_name": "",
                "second_logistic_service": "",
                "second_agency_fee": 0,
                "second_insurance": 0,
                "second_rate": 0,
                "awb": "",
                "autoresi_cashless_status": 0,
                "autoresi_awb": "",
                "autoresi_shipping_price": 0,
                "count_awb": 0,
                "isCashless": False,
                "is_fake_delivery": False
            },
            "destination": {
                "receiver_name": "maul",
                "receiver_phone": "085712345678",
                "address_street": "jalan gatot subroto kav 123456789",
                "address_district": "Jagakarsa",
                "address_city": "Kota Administrasi Jakarta Selatan",
                "address_province": "DKI Jakarta",
                "address_postal": "123456",
                "customer_address_id": 4649619,
                "district_id": 2263,
                "city_id": 175,
                "province_id": 13
            },
            "is_replacement": False,
            "replacement_multiplier": 0
        },
        "origin_info": {
            "sender_name": "I`nti.Cosmetic",
            "origin_province": 13,
            "origin_province_name": "DKI Jakarta",
            "origin_city": 174,
            "origin_city_name": "Kota Administrasi Jakarta Barat",
            "origin_address": "Jalan Letjen S. Parman, Palmerah, 11410",
            "origin_district": 2258,
            "origin_district_name": "Palmerah",
            "origin_postal_code": "",
            "origin_geo": "-6.190449999999999,106.79771419999997",
            "receiver_name": "maul",
            "destination_address": "jalan gatot subroto kav 123456789",
            "destination_province": 13,
            "destination_city": 175,
            "destination_district": 2263,
            "destination_postal_code": "123456",
            "destination_geo": ",",
            "destination_loc": {
                "lat": 0,
                "lon": 0
            }
        },
        "payment_info": {
            "payment_id": 11539459,
            "payment_ref_num": "PYM/20170720/XVII/VII/4999664",
            "payment_date": "2017-07-20T17:50:06Z",
            "payment_method": 0,
            "payment_status": "Verified",
            "payment_status_id": 2,
            "create_time": "2017-07-20T17:50:06Z",
            "pg_id": 12,
            "gateway_name": "Installment Payment",
            "discount_amount": 0,
            "voucher_code": "",
            "voucher_id": 0
        },
        "insurance_info": {
            "insurance_type": 0
        },
        "hold_info": None,
        "cancel_request_info": None,
        "create_time": "2017-07-20T17:50:58.061156Z",
        "shipping_date": None,
        "update_time": "2017-07-24T08:01:07.073696Z",
        "payment_date": "2017-07-20T17:50:58.061156Z",
        "delivered_date": None,
        "est_shipping_date": None,
        "est_delivery_date": None,
        "related_invoices": None,
        "custom_fields": None
    }
}
