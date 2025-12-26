# ============================================================
# Parser plugin system (future-proof)
# ============================================================

@dataclass(frozen=True)
class ParseContext:
    source: str                 # original input (path or URL)
    local_path: Path            # local file path used for pdfplumber
    sha256: str
    text: str
    lower: str
    region: str
    meter_type: str


class ContractParser:
    """
    Implement a new parser by subclassing ContractParser and registering it via
    @register_contract_parser.

    detect(ctx) returns a score in [0, 1]. Highest score wins.
    parse(ctx, contract) mutates contract fields.
    """
    name: str = "base"
    priority: int = 0  # tie-breaker

    def detect(self, ctx: ParseContext) -> float:
        return 0.0

    def parse(self, ctx: ParseContext, contract: "ElectricityContract") -> None:
        raise NotImplementedError


_PARSER_REGISTRY: List[Type[ContractParser]] = []


def register_contract_parser(cls: Type[ContractParser]) -> Type[ContractParser]:
    _PARSER_REGISTRY.append(cls)
    return cls


# ============================================================
# ElectricityContract (fields unchanged; parsing refactored)
# ============================================================

@dataclass
class ElectricityContract:
    """
    Contains all contract-related cost parameters.

    Units:
    - dual_* fields: c€/kWh
    - excise_duty / energy_contribution / green_power_fee / purchase_rate_*: €/kWh
    - *_fix / data_management_cost: €/year
    - dynamic_*_var_* multipliers: unitless
    - dynamic_*_fix_* adders: €/MWh (Belpex is €/MWh)
    """

    # Contract type label used for GridCost tariff selection
    contract_type: str = "DynamicTariff"  # "DualTariff" or "DynamicTariff"


    # ---  tariff parameters (c€/kWh) ---
    dual_cons_peak: float = 0.30
    dual_cons_offpeak: float = 0.20
    dual_inj_peak: float = -0.05
    dual_inj_offpeak: float = 0.0
    dual_fix: float = 100.7

    # --- Capacity tariff (€/kW/year) ---
    capacity_tariff_rate:  Dict[str, float] = field(default_factory=dict)

    # --- Dynamic tariff formula parameters (Belpex in €/MWh) ---
    dynamic_cons_var_peak: float = 1.0
    dynamic_cons_var_offpeak: float = 1.0
    dynamic_cons_fix_peak: float = 0.0
    dynamic_cons_fix_offpeak: float = 0.0
    dynamic_inj_var_peak: float = 0.0
    dynamic_inj_var_offpeak: float = 0.0
    dynamic_inj_fix_peak: float = 0.0
    dynamic_inj_fix_offpeak: float = 0.0
    dynamic_fix: float = 31.8

    green_power_fee: float = 0.0025 #EUR/kWh (Kost GSC+ Kost WKK)
    subscription_cost: float = 0.0 # EUR/month
	
    # --- Net components ---

    data_management_cost: Dict[str, float] = field(default_factory=dict)
    purchase_rate_injection: Dict[str, float] = field(default_factory=dict) # €/kWh ( injectietarief
    purchase_rate_consumption: Dict[str, float] = field(default_factory=dict) # (afnametarief enkelvoudig)
	
    #--- Heffingen
    energy_contribution: float = 0.0020417 # EURO/kWh (bijdrage op de energie)
    
    excise_duty_tiers: List[dict] = field(default_factory=lambda: [
        {"from_kwh": 0,     "to_kwh": 3000,    "consumer": 0.04748, "business": 0.01421},
        {"from_kwh": 3000,  "to_kwh": 20000,   "consumer": 0.04748, "business": 0.01421},
        {"from_kwh": 20000, "to_kwh": 50000,   "consumer": 0.04546, "business": 0.01209},
        {"from_kwh": 50000, "to_kwh": 1000000, "consumer": 0.04478, "business": 0.01139},
    ])  #TODO: adjust way of setting excise duty and implement
    contribution_energy_fund: float = 0.0 # EUR/month

    # --- Metadata ---
    contract_id: str = ""
    supplier: str = ""
    product_name: str = ""
    meter_type: str = ""
    language: str = ""
    valid_from: str = ""
    valid_to: str = ""
    source_pdf_path: str = ""
    source_pdf_sha256: str = ""
    parsed_at: str = ""
    notes: str = ""

    # -----------------------------
    # Constants / regex (not fields)
    # -----------------------------
    _MONTHS_NL: ClassVar[Dict[str, int]] = {
        "januari": 1, "februari": 2, "maart": 3, "april": 4, "mei": 5, "juni": 6,
        "juli": 7, "augustus": 8, "september": 9, "oktober": 10, "november": 11, "december": 12
    }

    _FORMULA_RE: ClassVar[re.Pattern] = re.compile(
        r"Belpex(?:_[A-Za-z]+)?\s*(?:\*|x)\s*(?P<mult>[0-9]+(?:[.,][0-9]+)?)\s*\)?\s*(?P<op>[+-])\s*€?\s*(?P<add>[+-]?[0-9]+(?:[.,][0-9]+)?)",
        flags=re.I,
    )

    # -----------------------------
    # General helpers
    # -----------------------------
    @staticmethod
    def _parse_eu_number(value: str, *, factor: float = 1.0) -> float:
        s = re.sub(r"[^0-9,.\-+]", "", str(value))
        if not s:
            raise ValueError(f"Could not parse number from {value!r}")
        if "," in s and "." in s:
            if s.rfind(",") > s.rfind("."):
                s = s.replace(".", "").replace(",", ".")
            else:
                s = s.replace(",", "")
        else:
            s = s.replace(",", ".")
        return float(s) * factor

    @staticmethod
    def _normalize(text: str) -> str:
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    @staticmethod
    def _sha256_bytes(b: bytes) -> str:
        return hashlib.sha256(b).hexdigest()

    @classmethod
    def _ensure_local_pdf(cls, pdf_path_or_url: str) -> Tuple[Path, Optional[Path], str]:
        s = str(pdf_path_or_url).strip()
        if s.lower().startswith(("http://", "https://")):
            import requests  # optional dependency
            r = requests.get(s, timeout=60)
            r.raise_for_status()
            sha = cls._sha256_bytes(r.content)
            tmp = Path(tempfile.gettempdir()) / f"electricity_contract_{sha[:16]}.pdf"
            tmp.write_bytes(r.content)
            return tmp, tmp, sha

        p = Path(s)
        if not p.exists():
            raise FileNotFoundError(s)
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        return p, None, sha

    @staticmethod
    def _read_pdf_text(local_pdf_path: str) -> str:
        from typing import List, Optional
        import pdfplumber

        parts: List[str] = []

        # Best-effort table detection (works well when tables have visible lines)
        table_settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "snap_tolerance": 3,
            "join_tolerance": 3,
            "edge_min_length": 3,
            "intersection_tolerance": 3,
            "text_tolerance": 3,
        }

        with pdfplumber.open(local_pdf_path) as pdf:
            for page_idx, page in enumerate(pdf.pages, start=1):
                # 1) Regular text
                t = page.extract_text() or ""
                if t.strip():
                    parts.append(f"[PAGE {page_idx} TEXT]\n{t.strip()}")

                # 2) Tables -> serialize as TSV so it's easy to ingest later
                try:
                    tables = page.extract_tables(table_settings=table_settings) or []
                except TypeError:
                    # compatibility with older pdfplumber versions
                    tables = page.extract_tables() or []

                for tbl_idx, table in enumerate(tables, start=1):
                    rows: List[str] = []
                    for row in (table or []):
                        if not row:
                            continue
                        cells = [((c or "").replace("\n", " ").strip()) for c in row]
                        while cells and cells[-1] == "":
                            cells.pop()
                        if any(cells):
                            rows.append("\t".join(cells))

                    tsv = "\n".join(rows).strip()
                    if tsv:
                        parts.append(f"[PAGE {page_idx} TABLE {tbl_idx} TSV]\n{tsv}")

        return "\n\n".join(parts).strip()


    @staticmethod
    def _detect_language(text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["tariefkaart", "abonnement", "bijdrage", "leveringsovereenkomst"]):
            return "NL"
        if any(w in t for w in ["contrat", "abonnement", "contribution", "redevance"]):
            return "FR"
        return ""

    @staticmethod
    def _detect_supplier(text: str) -> str:
        t = text.lower()
        if "belvus" in t:
            return "Belvus"
        if "bolt" in t or "boltenergie" in t:
            return "Bolt"
        if "energyvision" in t:
            return "EnergyVision"
        if "mega" in t:
            return "MEGA"
        return ""

    @staticmethod
    def _detect_product_name(text: str, supplier: str = "") -> str:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for ln in lines[:120]:
            if ln.startswith("[PAGE "):
                continue
            if re.match(r"Tariefkaart\b", ln, flags=re.I):
                continue
            if ln.upper() == "FLANDERS INTERNATIONAL AIRPORT":
                continue

            if re.search(r"\bFLOW\+?\s*EL\b", ln, flags=re.I):
                return "FLOW+ EL"
            if "Plenty Variabel Online" in ln:
                return "Plenty Variabel Online"
            if re.search(r"Offre\s+sp[ée]ciale\s+Testachats", ln, flags=re.I):
                return "Offre spéciale Testachats"

        if supplier:
            for ln in lines[:180]:
                if ln.startswith("[PAGE "):
                    continue
                if re.match(r"Tariefkaart\b", ln, flags=re.I):
                    continue
                if ln.upper() == "FLANDERS INTERNATIONAL AIRPORT":
                    continue
                if supplier.lower() in ln.lower():
                    continue
                if 3 < len(ln) < 80 and any(ch.isalpha() for ch in ln):
                    return ln
        return ""

    @classmethod
    def _detect_validity(cls, text: str) -> Tuple[str, str]:
        m = re.search(r"\b(" + "|".join(cls._MONTHS_NL.keys()) + r")\s+(\d{4})\b", text, flags=re.I)
        if not m:
            return "", ""
        month = cls._MONTHS_NL.get(m.group(1).lower())
        year = int(m.group(2))
        return (f"{year:04d}-{month:02d}-01", "") if month else ("", "")

    # -----------------------------
    # Extractors (reusable by parsers)
    # -----------------------------
    @classmethod
    def _extract_belpex_formulas(cls, text: str) -> Dict[str, List[Dict[str, Any]]]:
        cons: List[Dict[str, Any]] = []
        inj: List[Dict[str, Any]] = []

        for m in cls._FORMULA_RE.finditer(text):
            mult_str = (m.group("mult_pre") or m.group("mult_post") or "1")
            mult = cls._parse_eu_number(mult_str)

            add_raw = cls._parse_eu_number(m.group("add"))
            op = (m.group("op") or "+").strip()
            add = add_raw if op == "+" else -add_raw

            start = m.start()
            ctx = text[max(0, start - 180):start].lower()
            snippet = text[m.start():m.end()].lower()

            is_inj = False
            if "spp" in snippet or "spp" in ctx:
                is_inj = True
            elif "rlp" in snippet or "rlp" in ctx:
                is_inj = False
            elif any(k in ctx for k in ["inject", "injectie", "teruglever", "teruglevering"]):
                is_inj = True

            period = None
            ctx2 = text[max(0, start - 80):m.end() + 40].lower()
            if "nacht" in ctx2 and "dag" not in ctx2:
                period = "offpeak"
            elif "dag" in ctx2 and "nacht" not in ctx2:
                period = "peak"

            rec = {"period": period, "mult": mult, "add": add}
            (inj if is_inj else cons).append(rec)

        return {"cons": cons, "inj": inj}

    @staticmethod
    def _pick_peak_off(records: List[Dict[str, Any]]) -> Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]]:
        peak = next(((r["mult"], r["add"]) for r in records if r["period"] == "peak"), None)
        off = next(((r["mult"], r["add"]) for r in records if r["period"] == "offpeak"), None)
        if peak is None and off is None:
            if not records:
                return None, None
            v = (records[0]["mult"], records[0]["add"])
            return v, v
        return (peak or off), (off or peak)

    @staticmethod
    def _extract_subscription_annual_eur(text: str) -> Optional[float]:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        for ln in lines:
            l = ln.lower()
            if "abonn" in l and "maand" not in l and (("jaar" in l) or ("/jaar" in l) or ("€/an" in l) or ("jaarlijk" in l)):
                m = re.search(r"€\s*([0-9]+[.,]?[0-9]*)", ln)
                if m:
                    return ElectricityContract._parse_eu_number(m.group(1))

        for ln in lines:
            l = ln.lower()
            if "abonn" in l and (("maand" in l) or ("/mois" in l)):
                m = re.search(r"€\s*([0-9]+[.,]?[0-9]*)", ln)
                if m:
                    return round(ElectricityContract._parse_eu_number(m.group(1)) * 12, 6)

        return None

    @staticmethod
    def _extract_cents_per_kwh_to_eur_per_kwh(text: str, label_patterns: List[str]) -> Optional[float]:
        unit = r"(?:€\s*cent|€cent|cent|c€|€c)"
        for lab in label_patterns:
            # number BEFORE unit (common: "Energiebijdrage 0,20417 €cent/kWh")
            m = re.search(
                lab + r".{0,240}?([0-9]+(?:[.,][0-9]+)?)\s*" + unit + r"\s*/?\s*kwh",
                text,
                flags=re.I | re.S,
            )
            if m:
                return ElectricityContract._parse_eu_number(m.group(1), factor=0.01)

            # unit BEFORE number (rarer but keep compatibility)
            m = re.search(
                lab + r".{0,240}?" + unit + r"\s*([0-9]+(?:[.,][0-9]+)?)\s*/?\s*kwh",
                text,
                flags=re.I | re.S,
            )
            if m:
                return ElectricityContract._parse_eu_number(m.group(1), factor=0.01)
        return None

    @staticmethod
    def _extract_green_fees(text: str, region: str = "VL") -> Tuple[Optional[float], Optional[float]]:
        region = region.upper()

        # EnergyVision style combined line:
        m = re.search(r"Kosten\s+GSC\s+en\s+WKC\s+bedragen\s*([0-9]+(?:[.,][0-9]+)?)\s*€?\s*cent/kWh", text, flags=re.I)
        if m:
            combined = ElectricityContract._parse_eu_number(m.group(1), factor=0.01)
            return combined, 0.0  # treat as all-in so sum() works

        # existing logic ...
        m = re.search(r"\bGSC\b\s*€c\s*([0-9]+[.,][0-9]+)", text, flags=re.I)
        gsc = ElectricityContract._parse_eu_number(m.group(1), factor=0.01) if m else None
        m = re.search(r"\bWKK\b\s*€c\s*([0-9]+[.,][0-9]+)", text, flags=re.I)
        wkk = ElectricityContract._parse_eu_number(m.group(1), factor=0.01) if m else None
        if gsc is not None or wkk is not None:
            return gsc, wkk

        gsc = None
        m = re.search(
            r"Groene certificaten.*?([0-9]+[.,][0-9]+)\s+([0-9]+[.,][0-9]+)\s+([0-9]+[.,][0-9]+)",
            text,
            flags=re.I | re.S,
        )
        if m:
            vals = [ElectricityContract._parse_eu_number(m.group(i)) for i in (1, 2, 3)]  # c€/kWh
            idx = {"VL": 0, "WAL": 1, "BRU": 2}.get(region, 0)
            gsc = vals[idx] / 100.0

        wkk = None
        m = re.search(r"WKK\s*\(c.?/?kWh\).*?([0-9]+[.,][0-9]+)", text, flags=re.I | re.S)
        if m:
            wkk = ElectricityContract._parse_eu_number(m.group(1), factor=0.01)

        return gsc, wkk
    
    @classmethod
    def _extract_dual_prices_cent(cls, text: str) -> Dict[str, float]:
        """
        Best-effort dual extraction into *c€/kWh* fields.
        """
        res: Dict[str, float] = {}

        # Mega FR style mono: "Compteur mono-horaire 11.16 1.98" (usually c€/kWh)
        m = re.search(r"Compteur\s+mono[-\s]?horaire\s+([0-9][0-9.,]*)\s+([0-9][0-9.,]*)", text, flags=re.I)
        if m:
            cons_c = cls._parse_eu_number(m.group(1))  # assume c€/kWh
            inj_c = cls._parse_eu_number(m.group(2))
            res.update({
                "dual_cons_peak": cons_c,
                "dual_cons_offpeak": cons_c,
                "dual_inj_peak": -inj_c,
                "dual_inj_offpeak": -inj_c,
            })
            return res

        # Mega FR style bi: 4 numbers
        m = re.search(
            r"Compteur\s+bi[-\s]?horaire\s+([0-9][0-9.,]*)\s+([0-9][0-9.,]*)\s+([0-9][0-9.,]*)\s+([0-9][0-9.,]*)",
            text, flags=re.I
        )
        if m:
            res.update({
                "dual_cons_peak": cls._parse_eu_number(m.group(1)),
                "dual_cons_offpeak": cls._parse_eu_number(m.group(2)),
                "dual_inj_peak": -cls._parse_eu_number(m.group(3)),
                "dual_inj_offpeak": -cls._parse_eu_number(m.group(4)),
            })
            return res

        # Generic NL-ish (if present)
        def find(label: str) -> Optional[float]:
            mm = re.search(label + r".{0,60}?([0-9]+[.,][0-9]+)", text, flags=re.I | re.S)
            return cls._parse_eu_number(mm.group(1)) if mm else None

        cd = find(r"(Afname\s+dag|Verbruik\s+dag|Dag(?:tarief)?)")
        cn = find(r"(Afname\s+nacht|Verbruik\s+nacht|Nacht(?:tarief)?)")
        if cd is not None and cn is not None:
            res["dual_cons_peak"] = cd
            res["dual_cons_offpeak"] = cn

        iday = find(r"(Injectie\s+dag|Teruglever\s+dag)")
        inight = find(r"(Injectie\s+nacht|Teruglever\s+nacht)")
        if iday is not None and inight is not None:
            res["dual_inj_peak"] = -iday
            res["dual_inj_offpeak"] = -inight
        elif iday is not None:
            res["dual_inj_peak"] = -iday
            res["dual_inj_offpeak"] = -iday

        return res

    # -----------------------------
    # Public utils
    # -----------------------------
    def as_dict(self, *, include_metadata: bool = False) -> Dict[str, Any]:
        d = asdict(self)
        if include_metadata:
            return d
        for k in (
            "contract_id", "supplier", "product_name", "meter_type", "language",
            "valid_from", "valid_to", "source_pdf_path", "source_pdf_sha256",
            "parsed_at", "notes",
        ):
            d.pop(k, None)
        return d

    def _fingerprint_dict(self) -> Dict[str, Any]:
        d = self.as_dict(include_metadata=False)
        for k, v in list(d.items()):
            if isinstance(v, float):
                d[k] = round(v, 12)
        return d

    # -----------------------------
    # Parser selection + common-field pass
    # -----------------------------
    @classmethod
    def _select_parser(cls, ctx: ParseContext, *, force: Optional[str] = None) -> Tuple[ContractParser, float]:
        candidates: List[Tuple[float, int, ContractParser]] = []
        for parser_cls in _PARSER_REGISTRY:
            parser = parser_cls()
            if force and parser.name != force:
                continue
            score = float(parser.detect(ctx) or 0.0)
            candidates.append((score, getattr(parser, "priority", 0), parser))

        if not candidates:
            return _FallbackParser(), 0.0

        candidates.sort(reverse=True, key=lambda x: (x[0], x[1]))
        best_score, _, best_parser = candidates[0]
        if best_score <= 0.0:
            return _FallbackParser(), 0.0
        return best_parser, best_score

    @classmethod
    def _apply_common_fields(cls, ctx: ParseContext, c: "ElectricityContract") -> None:
        sub = cls._extract_subscription_annual_eur(ctx.text)
        if sub is not None:
            if c.contract_type == "DynamicTariff":
                c.dynamic_fix = sub
            else:
                c.dual_fix = sub

        exc = cls._extract_cents_per_kwh_to_eur_per_kwh(
            ctx.text,
            [
                r"Bijzondere accijns",
                r"accijns op Energie",
                r"Federale\s+Accijns",
                r"\bAccijns\b",
                r"\bAccise\b",
                r"\baccise\b",
                r"Accise sur",
            ],
        )
        if exc is not None:
            c.excise_duty = exc

        eco = cls._extract_cents_per_kwh_to_eur_per_kwh(
            ctx.text,
            [
                r"Energiebijdrage",
                r"Bijdrage op Energie",
                r"Bijdrage op de energie",
                r"Contribution.*\b(é|e)nergie",
            ],
        )
        if eco is not None:
            c.energy_contribution = eco

        gsc, wkk = cls._extract_green_fees(ctx.text, region=ctx.region)
        if gsc is not None or wkk is not None:
            c.green_power_fee = (gsc or 0.0) + (wkk or 0.0)


    # -----------------------------
    # Single entry point
    # -----------------------------
    @classmethod
    def _from_pdf(
        cls,
        pdf_path: str,
        *,
        region: str = "VL",
        meter_type: str = "",
        text_override: Optional[str] = None,
        force_parser: Optional[str] = None,  # e.g. "mega_testachats_brussels"
    ) -> "ElectricityContract":
        local_path, tmp_path, sha = cls._ensure_local_pdf(pdf_path)

        text = text_override if text_override is not None else cls._read_pdf_text(str(local_path))
        text = cls._normalize(text)
        ctx = ParseContext(
            source=str(pdf_path),
            local_path=local_path,
            sha256=sha,
            text=text,
            lower=text.lower(),
            region=region,
            meter_type=meter_type,
        )

        c = cls()  # defaults

        # metadata (generic detection; parsers may override)
        c.source_pdf_path = str(pdf_path)
        c.source_pdf_sha256 = sha
        c.parsed_at = datetime.now().isoformat(timespec="seconds")
        c.language = cls._detect_language(text)
        c.meter_type = meter_type or c.meter_type #TODO: improve detection?
        c.supplier = cls._detect_supplier(text)
        c.product_name = cls._detect_product_name(text, supplier=c.supplier)
        c.valid_from, c.valid_to = cls._detect_validity(text)
        base = "|".join([c.supplier, c.product_name, c.valid_from, sha[:12]])
        c.contract_id = hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]

        parser, score = cls._select_parser(ctx, force=force_parser)
        parser.parse(ctx, c)

        cls._apply_common_fields(ctx, c)

        c.notes = f"parser={parser.name} score={score:.2f}"
        extra_notes = (c.notes or "").strip()
        c.notes = f"parser={parser.name} score={score:.2f}"
        if extra_notes:
            c.notes += f" | {extra_notes}"
        if tmp_path is not None:
            c.notes += " source=downloaded_url"
        return c

    @classmethod
    def from_pdf(cls, pdf_path: str, **kwargs: Any) -> "ElectricityContract":
        return cls._from_pdf(pdf_path, **kwargs)


# ============================================================
# Built-in parsers
# ============================================================

@register_contract_parser
class MegaTestachatsBrusselsParser(ContractParser):
    name = "mega_testachats_brussels"
    priority = 100

    def detect(self, ctx: ParseContext) -> float:
        if "offre spéciale testachats" in ctx.lower and "sibelga" in ctx.lower:
            return 0.98
        if "testachats" in ctx.lower and "mega" in ctx.lower:
            return 0.85
        return 0.0

    def parse(self, ctx: ParseContext, c: ElectricityContract) -> None:
        c.supplier = c.supplier or "MEGA"
        if not c.product_name:
            c.product_name = "Offre spéciale Testachats"
        c.contract_type = "DualTariff"

        dual = ElectricityContract._extract_dual_prices_cent(ctx.text)
        for k, v in dual.items():
            setattr(c, k, v)

        # Specific tax table (FR) if present:
        # "Consommation entre 0 et 3000 kWh 5.03288 0.20417 c€/kWh"
        m = re.search(
            r"Consommation\s+entre\s+0\s+et\s+3000\s*kWh\s+([0-9][0-9.,]*)\s+([0-9][0-9.,]*)",
            ctx.text,
            flags=re.I,
        )
        if m:
            c.excise_duty = ElectricityContract._parse_eu_number(m.group(1), factor=0.01)
            c.energy_contribution = ElectricityContract._parse_eu_number(m.group(2), factor=0.01)

        # Fixed fee line (FR)
        m = re.search(r"Redevance\s+fixe\s*\(€/an\)\s+([0-9][0-9.,]*)", ctx.text, flags=re.I)
        if m:
            c.dual_fix = ElectricityContract._parse_eu_number(m.group(1))


@register_contract_parser
class BelpexDynamicParser(ContractParser):
    name = "belpex_dynamic_generic"
    priority = 50

    def detect(self, ctx: ParseContext) -> float:
        formulas = ElectricityContract._extract_belpex_formulas(ctx.text)
        if formulas["cons"] or formulas["inj"]:
            # boost if RLP/SPP markers appear (common in BE contracts)
            bonus = 0.1 if ("rlp" in ctx.lower or "spp" in ctx.lower) else 0.0
            return min(1.0, 0.80 + bonus)
        return 0.0

    def parse(self, ctx: ParseContext, c: ElectricityContract) -> None:
        c.contract_type = "DynamicTariff"
        formulas = ElectricityContract._extract_belpex_formulas(ctx.text)

        cons_peak, cons_off = ElectricityContract._pick_peak_off(formulas["cons"])
        if cons_peak:
            c.dynamic_cons_var_peak, c.dynamic_cons_fix_peak = cons_peak
        if cons_off:
            c.dynamic_cons_var_offpeak, c.dynamic_cons_fix_offpeak = cons_off

        inj_peak, inj_off = ElectricityContract._pick_peak_off(formulas["inj"])
        if inj_peak:
            c.dynamic_inj_var_peak, c.dynamic_inj_fix_peak = inj_peak
        if inj_off:
            c.dynamic_inj_var_offpeak, c.dynamic_inj_fix_offpeak = inj_off


@register_contract_parser
class GenericDualTariffParser(ContractParser):
    name = "dual_generic"
    priority = 10

    def detect(self, ctx: ParseContext) -> float:
        # Only claim dual if no Belpex formulas
        formulas = ElectricityContract._extract_belpex_formulas(ctx.text)
        if formulas["cons"] or formulas["inj"]:
            return 0.0
        if any(k in ctx.lower for k in ["mono-horaire", "bi-horaire", "dagtarief", "nachttarief", "afname dag", "afname nacht"]):
            return 0.55
        return 0.25

    def parse(self, ctx: ParseContext, c: ElectricityContract) -> None:
        c.contract_type = "DualTariff"
        dual = ElectricityContract._extract_dual_prices_cent(ctx.text)
        for k, v in dual.items():
            setattr(c, k, v)

@register_contract_parser
class EnergyVisionStroomVanTZeetjeParser(ContractParser):
    name = "energyvision_stroomvantzeetje"
    priority = 120

    def detect(self, ctx: ParseContext) -> float:
        t = ctx.lower
        if "energyvision" in t and ("stroom van" in t and "zeetje" in t):
            return 0.99
        if "stroomvantzeetje" in t:
            return 0.99
        if "energyvision" in t and "tariefkaart" in t:
            return 0.80
        return 0.0

    def parse(self, ctx: ParseContext, c: ElectricityContract) -> None:
        c.supplier = c.supplier or "EnergyVision"
        c.contract_type = "DynamicTariff"

        # Product name: line after "Tariefkaart <month year>"
        m = re.search(r"Tariefkaart\s+[^\n]+\n([^\n]+)", ctx.text, flags=re.I)
        if m and not c.product_name:
            c.product_name = m.group(1).strip()

        # Fixed yearly fee: "Vaste vergoeding 50 €/jaar"
        m = re.search(r"Vaste vergoeding\s*([0-9]+(?:[.,][0-9]+)?)\s*€?\s*/\s*jaar", ctx.text, flags=re.I)
        if m:
            c.dynamic_fix = ElectricityContract._parse_eu_number(m.group(1))

        # Parse Belpex formulas into dynamic_* (now works with "1,12 x Belpex- RLP-M + 20" etc.)
        BelpexDynamicParser().parse(ctx, c)

        # Estimated rates printed on the card (store as purchase_rate_* €/kWh)
        m = re.search(
            r"Groene stroom van het net\s*\(>\s*1\.?000\s*kWh[^)]*\)\s*([0-9]+(?:[.,][0-9]+)?)\s*€?\s*cent/kWh",
            ctx.text,
            flags=re.I,
        )
        if m:
            c.purchase_rate_consumption = ElectricityContract._parse_eu_number(m.group(1), factor=0.01)

        m = re.search(r"Injectie\s*-\s*variabel\s*([0-9]+(?:[.,][0-9]+)?)\s*€?\s*cent/kWh", ctx.text, flags=re.I)
        if m:
            c.purchase_rate_injection = ElectricityContract._parse_eu_number(m.group(1), factor=0.01)

        # Combined GSC+WKC fee
        m = re.search(r"Kosten\s+GSC\s+en\s+WKC\s+bedragen\s*([0-9]+(?:[.,][0-9]+)?)\s*€?\s*cent/kWh", ctx.text, flags=re.I)
        if m:
            c.green_power_fee = ElectricityContract._parse_eu_number(m.group(1), factor=0.01)

        # Extra “important” bits that don’t fit fields -> notes
        extras = []

        m = re.search(r"welkomstkorting\s*([0-9]+(?:[.,][0-9]+)?)\s*(?:€|euro)", ctx.text, flags=re.I)
        if m:
            extras.append(f"welcome_discount_eur={ElectricityContract._parse_eu_number(m.group(1))}")

        m = re.search(
            r"Groene stroom van het net\s*\(<\s*1\.?000\s*kWh[^)]*\)\s*([0-9]+(?:[.,][0-9]+)?)\s*€?\s*cent/kWh",
            ctx.text,
            flags=re.I,
        )
        if m:
            extras.append(f"fixed_first_1000kwh_cent_per_kwh={ElectricityContract._parse_eu_number(m.group(1))}")

        # Optional: domiciliation monthly energy-fund fee (keep as info)
        m_dom = re.search(r"Standaard tarief gedomicilieerd:\s*([0-9]+(?:[.,][0-9]+)?)\s*€/maand", ctx.text, flags=re.I)
        m_nodom = re.search(r"Standaard tarief niet-gedomicilieerd:\s*([0-9]+(?:[.,][0-9]+)?)\s*€/maand", ctx.text, flags=re.I)
        if m_dom:
            extras.append(f"energy_fund_fee_domiciled_eur_per_month={ElectricityContract._parse_eu_number(m_dom.group(1))}")
        if m_nodom:
            extras.append(f"energy_fund_fee_not_domiciled_eur_per_month={ElectricityContract._parse_eu_number(m_nodom.group(1))}")

        if extras:
            c.notes = " ; ".join(extras)

class _FallbackParser(ContractParser):
    name = "fallback"
    priority = -1

    def detect(self, ctx: ParseContext) -> float:
        return 0.0

    def parse(self, ctx: ParseContext, c: ElectricityContract) -> None:
        # Final fallback: if Belpex exists -> dynamic else dual
        formulas = ElectricityContract._extract_belpex_formulas(ctx.text)
        if formulas["cons"] or formulas["inj"]:
            BelpexDynamicParser().parse(ctx, c)
        else:
            GenericDualTariffParser().parse(ctx, c)


# Convenience function: _from_pdf("link_to_pdf")
def _from_pdf(pdf_path: str, **kwargs: Any) -> ElectricityContract:
    return ElectricityContract._from_pdf(pdf_path, **kwargs)


"""
How to add a new contract type later:

@register_contract_parser
class MyNewSupplierParser(ContractParser):
    name = "my_supplier_xyz"
    priority = 80  # higher = wins ties

    def detect(self, ctx: ParseContext) -> float:
        return 0.95 if "supplier xyz" in ctx.lower and "tariefkaart" in ctx.lower else 0.0

    def parse(self, ctx: ParseContext, c: ElectricityContract) -> None:
        c.supplier = "Supplier XYZ"
        c.contract_type = "DynamicTariff"  # or "DualTariff"
        # Extract your fields here using ctx.text / ctx.lower and the shared helpers.
"""


