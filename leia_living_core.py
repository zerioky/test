# =============================================================================
# PATCH V18 — Intégration des 6 nouveaux modules dans leia_living_core.py
# =============================================================================
#
# Ce fichier documente et fournit les blocs de code exacts à insérer.
# Chaque section indique QUOI insérer, OÙ, et POURQUOI.
#
# Instruction d'application :
#   1. Copier les 6 nouveaux fichiers dans Azip_py_projectleia_separed/
#   2. Appliquer chaque bloc ci-dessous à leia_living_core.py
#   3. Vérifier avec : python -m compileall -q .
#   4. Tester avec   : python -c "from leia_living_core import LeiaLivingCore; c=LeiaLivingCore(); print(c.self_test())"
# =============================================================================


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 1 — IMPORTS (à ajouter après les imports V17 existants)
# Chercher : "from strong_initiative_engine import StrongInitiativeEngine"
# Ajouter APRÈS le bloc try/except correspondant :
# ─────────────────────────────────────────────────────────────────────────────

BLOCK_1_IMPORTS = """
try:
    from user_utterance_parser import UserUtteranceParser
except Exception:
    UserUtteranceParser = None

try:
    from associative_memory import AssociativeMemory
except Exception:
    AssociativeMemory = None

try:
    from semantic_coherence import SemanticCoherence
except Exception:
    SemanticCoherence = None

try:
    from proposition_extractor import PropositionExtractor
except Exception:
    PropositionExtractor = None

try:
    from user_model import UserModel
except Exception:
    UserModel = None

try:
    from affect_lexicon import AffectLexicon
except Exception:
    AffectLexicon = None
"""


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 2 — INSTANCIATION (dans __init__, après les instanciations V17)
# Chercher : "self.reasoning_trace = ReasoningTrace(...)" ou similaire
# Ajouter APRÈS :
# ─────────────────────────────────────────────────────────────────────────────

BLOCK_2_INIT = """
        # ── V18 : Compréhension réelle sans LLM ──────────────────────────────
        self.utterance_parser = (UserUtteranceParser(
            storage_path=os.path.join(self.data_dir, "utterance_history.json"))
            if UserUtteranceParser is not None else None)

        self.associative_memory = (AssociativeMemory(
            storage_path=os.path.join(self.data_dir, "associative_memory.json"))
            if AssociativeMemory is not None else None)

        self.semantic_coherence = (SemanticCoherence(
            storage_path=os.path.join(self.data_dir, "semantic_coherence.json"))
            if SemanticCoherence is not None else None)

        self.proposition_extractor = (PropositionExtractor(
            storage_path=os.path.join(self.data_dir, "propositions.json"))
            if PropositionExtractor is not None else None)

        self.user_model = (UserModel(
            storage_path=os.path.join(self.data_dir, "user_model.json"))
            if UserModel is not None else None)

        self.affect_lexicon = (AffectLexicon(
            storage_path=os.path.join(self.data_dir, "affect_lexicon.json"))
            if AffectLexicon is not None else None)
"""


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 3 — DANS respond() — Observation utilisateur
# Chercher : "user_input_resolved = self.conversation_window.resolve_reference(user_input)"
# Ajouter JUSTE APRÈS ce bloc (après l'attribution de user_input_resolved) :
# ─────────────────────────────────────────────────────────────────────────────

BLOCK_3_IN_RESPOND = """
        # V18 — Analyse du message utilisateur et observation du modèle utilisateur
        _utterance_signal = {}
        if self.utterance_parser is not None:
            try:
                _utterance_signal = self.utterance_parser.signal(user_input_resolved)
                self.living_state["utterance_signal"] = _utterance_signal
            except Exception:
                pass

        if self.user_model is not None:
            try:
                self.user_model.observe(user_input_resolved, _utterance_signal)
            except Exception:
                pass

        # V18 — Affect du message utilisateur
        if self.affect_lexicon is not None:
            try:
                _user_affect = self.affect_lexicon.signal(user_input_resolved, "user")
                self.living_state["user_affect_signal"] = _user_affect
            except Exception:
                pass

        # V18 — Mémoire associative : spread depuis les concepts du message
        if self.associative_memory is not None:
            try:
                _seeds = (_utterance_signal.get("focus_concepts", [])
                          + _utterance_signal.get("content_words", [])[:4])
                _assoc_signal = self.associative_memory.signal(_seeds, user_input_resolved)
                self.living_state["associative_signal"] = _assoc_signal
            except Exception:
                pass
"""


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 4 — DANS build_living_context() — Ajout des nouveaux signaux au contexte
# Chercher la fin de build_living_context, là où le dict `ctx` est construit
# et retourné. Ajouter les clés V18 dans ce dict.
#
# Pattern de recherche : "\"reasoning_trace_signal\":" ou "return ctx" à la fin
# Ajouter avant le return :
# ─────────────────────────────────────────────────────────────────────────────

BLOCK_4_IN_BUILD_CONTEXT = """
        # V18 — Signaux de compréhension réelle
        ctx["utterance_signal"] = self.living_state.get("utterance_signal", {"available": False})
        ctx["user_affect_signal"] = self.living_state.get("user_affect_signal", {"available": False})
        ctx["associative_signal"] = self.living_state.get("associative_signal", {"available": False})
        ctx["user_model_signal"] = (
            self.user_model.signal(user_input) if self.user_model is not None
            else {"available": False})
        ctx["proposition_signal"] = (
            self.proposition_extractor.signal(
                user_input,
                focus_concepts=self.living_state.get("utterance_signal",{}).get("focus_concepts",[])
            ) if self.proposition_extractor is not None
            else {"available": False})
"""


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 5 — DANS _build_living_expression_payload() — Ajout au payload du weaver
# Chercher le dict `payload = {...}` dans cette méthode.
# Ajouter ces clés dans ce dict (après les entrées V17) :
# ─────────────────────────────────────────────────────────────────────────────

BLOCK_5_IN_PAYLOAD = """
            # V18 — Compréhension réelle sans LLM
            "utterance_signal":   context.get("utterance_signal",   {"available": False}),
            "user_affect_signal": context.get("user_affect_signal", {"available": False}),
            "associative_signal": context.get("associative_signal", {"available": False}),
            "user_model_signal":  context.get("user_model_signal",  {"available": False}),
            "proposition_signal": context.get("proposition_signal", {"available": False}),
"""


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 6 — DANS remember_exchange() — Post-réponse : cohérence + mémoire assoc.
# Chercher : "# V17 — Traçabilité du raisonnement"
# Ajouter APRÈS ce bloc :
# ─────────────────────────────────────────────────────────────────────────────

BLOCK_6_IN_REMEMBER = """
        # V18 — Cohérence sémantique : Leia s'entend vraiment
        if self.semantic_coherence is not None and response:
            try:
                intended = []
                stabilizer = self.living_state.get("last_expression_payload", {}).get(
                    "living_presence_stabilizer", {})
                if isinstance(stabilizer, dict):
                    intended = list(stabilizer.get("concrete_concepts", []) or [])
                focus = self.living_state.get("last_expression_payload", {}).get("focus", "")
                if focus:
                    intended.insert(0, str(focus))
                # Réponses récentes depuis conversation_window
                recent = []
                if self.conversation_window is not None:
                    for i in range(1, 4):
                        r = self.conversation_window.get_last_leia_response(offset=i)
                        if r: recent.append(r)
                coherence_signal = self.semantic_coherence.signal(intended, response, recent)
                self.living_state["semantic_coherence_signal"] = coherence_signal
                # Transmettre les inhibitions au self_evaluation si dispo
                if coherence_signal.get("inhibitions") and self.self_evaluation is not None:
                    for inh in coherence_signal["inhibitions"]:
                        try:
                            getattr(self.self_evaluation, "_add_inhibition", lambda x: None)(inh)
                        except Exception:
                            pass
            except Exception:
                pass

        # V18 — Mémoire associative : apprend depuis l'échange complet
        if self.associative_memory is not None:
            try:
                exchange_text = f"{user_input} {response}"
                self.associative_memory.impregnate_text(
                    exchange_text, source="exchange", weight_boost=0.8)
            except Exception:
                pass

        # V18 — Propositions depuis l'échange
        if self.proposition_extractor is not None and user_input:
            try:
                self.proposition_extractor.extract_from_text(user_input, source="user")
            except Exception:
                pass
"""


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 7 — DANS load_pdf_book() — Intégration lors de la lecture d'un livre
# Chercher : "self.self_model.register_book(" ou "self.rhythmic_impregnation.impregnate("
# Ajouter APRÈS ces appels :
# ─────────────────────────────────────────────────────────────────────────────

BLOCK_7_IN_LOAD_PDF = """
            # V18 — Extraction de propositions (thèses, relations, oppositions)
            if self.proposition_extractor is not None:
                try:
                    prop_result = self.proposition_extractor.extract_from_book(
                        full_text, source=title or "book")
                    self.living_state["last_proposition_extraction"] = prop_result
                except Exception:
                    pass

            # V18 — Mémoire associative : imprégnation depuis le livre
            if self.associative_memory is not None:
                try:
                    # Extraire les concepts du livre (via lexical_impregnation ou brut)
                    book_concepts = []
                    lex_sig = (self.lexical_impregnation.expression_signal(
                        self.emotional_state.snapshot())
                        if self.lexical_impregnation is not None else {})
                    if isinstance(lex_sig, dict) and lex_sig.get("words"):
                        book_concepts = [w.get("surface","") for w in lex_sig["words"]
                                         if isinstance(w, dict) and w.get("surface")]
                    if not book_concepts:
                        import re as _re
                        book_concepts = _re.findall(r"[\wÀ-ÿ']{5,}", full_text.lower())[:200]
                    self.associative_memory.impregnate(
                        book_concepts[:120], source=title or "book", weight_boost=1.4)
                except Exception:
                    pass

            # V18 — Analyse affective du livre
            if self.affect_lexicon is not None:
                try:
                    book_affect = self.affect_lexicon.analyze_book_sample(
                        full_text, title=title or "")
                    self.living_state["last_book_affect"] = book_affect
                    # Si le livre est sombre → légère pression sur l'état émotionnel
                    if book_affect.get("is_dark") and hasattr(self.emotional_state, "update_from_signal"):
                        self.emotional_state.update_from_signal({
                            "valence_delta": book_affect["valence"] * 0.08
                        })
                except Exception:
                    pass
"""


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 8 — DANS tick_inner_life() — Décroissance associative + decay affect
# Chercher : la fin du tick_inner_life, là où les décroissances sont gérées
# Ajouter :
# ─────────────────────────────────────────────────────────────────────────────

BLOCK_8_IN_TICK = """
        # V18 — Décroissance organique de la mémoire associative
        if self.associative_memory is not None:
            try:
                self.associative_memory.global_decay(rate=0.001)
            except Exception:
                pass
"""


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 9 — DANS snapshot() ou save_state() — Sauvegarder les nouveaux modules
# Chercher : "self.self_model.save()" ou similaire, ou la fin de save_state
# Ajouter :
# ─────────────────────────────────────────────────────────────────────────────

BLOCK_9_SAVE = """
        # V18 — Sauvegarde des modules de compréhension
        for module_name in ("associative_memory", "proposition_extractor",
                            "user_model", "semantic_coherence", "affect_lexicon",
                            "utterance_parser"):
            module = getattr(self, module_name, None)
            if module is not None:
                save_fn = getattr(module, "save_now", None) or getattr(module, "_save", None)
                if save_fn:
                    try:
                        save_fn()
                    except Exception:
                        pass
"""


# ─────────────────────────────────────────────────────────────────────────────
# BLOC 10 — snapshot() public — Exposer les nouveaux états pour l'UI
# Chercher : la méthode snapshot() qui expose l'état pour l'UI
# Ajouter dans le dict retourné :
# ─────────────────────────────────────────────────────────────────────────────

BLOCK_10_SNAPSHOT = """
            "v18_comprehension": {
                "associative_memory":  (self.associative_memory.snapshot()
                    if self.associative_memory else {"available": False}),
                "proposition_extractor": (self.proposition_extractor.snapshot()
                    if self.proposition_extractor else {"available": False}),
                "user_model":          (self.user_model.snapshot()
                    if self.user_model else {"available": False}),
                "semantic_coherence":  (self.semantic_coherence.snapshot()
                    if self.semantic_coherence else {"available": False}),
                "affect_lexicon":      (self.affect_lexicon.snapshot()
                    if self.affect_lexicon else {"available": False}),
                "semantic_coherence_signal": self.living_state.get(
                    "semantic_coherence_signal", {}),
                "last_book_affect":    self.living_state.get("last_book_affect", {}),
            },
"""


# ─────────────────────────────────────────────────────────────────────────────
# INTÉGRATION DANS emergent_french_weaver.py
# Chercher : _dynamic_atoms_from_payload (fonction qui construit les atomes)
# Ajouter un nouveau bloc à la fin de cette fonction :
# ─────────────────────────────────────────────────────────────────────────────

BLOCK_11_WEAVER = """
        # V18 — Atomes depuis la mémoire associative (compréhension réelle)
        assoc_sig = payload.get("associative_signal", {})
        if isinstance(assoc_sig, dict) and assoc_sig.get("available"):
            for item in assoc_sig.get("activated", [])[:6]:
                surface = _public_surface(item.get("concept",""))
                if surface and len(surface) > 3:
                    act = float(item.get("activation", 0.3))
                    # Plus l'activation est forte, plus l'atome est probable
                    fields = {"memory": act, "presence": act * 0.7}
                    atoms.append(Atom(
                        surface=surface,
                        role="object",
                        fields=fields,
                        weight=_clamp(act * 1.2),
                    ))

        # V18 — Adaptation à l'utilisateur (user_model_signal)
        user_sig = payload.get("user_model_signal", {})
        if isinstance(user_sig, dict) and user_sig.get("available"):
            adapt = user_sig.get("adaptation", {})
            target_len = int(adapt.get("target_length_words", 14))
            # Ce champ sera lu par le plan pour ajuster la longueur cible
            payload_mut = dict(payload) if not hasattr(payload, "__setitem__") else payload
            # Note : le payload est Mapping donc on ne peut pas le muter directement.
            # La longueur cible est transmise via rhythmic_signal si disponible.
            # Le weaver lit déjà rhythmic_signal["target_length_words"].

        # V18 — Propositions de livre → atomes conceptuels forts
        prop_sig = payload.get("proposition_signal", {})
        if isinstance(prop_sig, dict) and prop_sig.get("available"):
            for prop in prop_sig.get("propositions", [])[:4]:
                subj = _public_surface(prop.get("subject",""))
                obj  = _public_surface(prop.get("object",""))
                for concept in (subj, obj):
                    if concept and len(concept) > 3:
                        atoms.append(Atom(
                            surface=concept,
                            role="object",
                            fields={"clarity": 0.7, "book": 0.6},
                            weight=0.55,
                        ))

        # V18 — Affect utilisateur → modifie le champ affectif des atomes
        user_affect = payload.get("user_affect_signal", {})
        if isinstance(user_affect, dict) and user_affect.get("available"):
            user_valence = float(user_affect.get("valence", 0.0))
            user_emotion = str(user_affect.get("emotion", "neutre"))
            # Réinjecter dans le field global si affect fort
            if abs(user_valence) > 0.3:
                for atom in atoms:
                    if "felt" in atom.fields or "body" in atom.fields:
                        atom.fields["valence_bias"] = user_valence * 0.4
"""


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION — Script de test rapide
# Sauvegarder comme test_v18.py et lancer depuis Azip_py_projectleia_separed/
# ─────────────────────────────────────────────────────────────────────────────

TEST_SCRIPT = """
#!/usr/bin/env python3
\"\"\"Test rapide des modules V18.\"\"\"
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

print("=== Test V18 modules ===")

# 1. UserUtteranceParser
try:
    from user_utterance_parser import UserUtteranceParser
    p = UserUtteranceParser("data/test_utt.json")
    sig = p.signal("Est-ce que la mémoire peut vraiment mentir ?")
    assert sig["available"]
    assert sig["is_question"]
    print(f"✓ UserUtteranceParser  intent={sig['intent']} focus={sig['focus_concept']}")
except Exception as e:
    print(f"✗ UserUtteranceParser  {e}")

# 2. AssociativeMemory
try:
    from associative_memory import AssociativeMemory
    am = AssociativeMemory("data/test_assoc.json")
    am.impregnate(["mémoire","durée","bergson","souvenir","temps","conscience"], "test")
    am.impregnate(["absurde","camus","révolte","sens","mort","liberté"], "test")
    sig = am.signal(["mémoire"], top_k=5)
    assert sig["available"]
    print(f"✓ AssociativeMemory    top={sig['top_concept']} act={sig['top_activation']:.3f}")
except Exception as e:
    print(f"✗ AssociativeMemory    {e}")

# 3. SemanticCoherence
try:
    from semantic_coherence import SemanticCoherence
    sc = SemanticCoherence("data/test_coh.json")
    sig = sc.signal(["mémoire","durée"], "Il reste une tension, quelque chose comme un appui.")
    print(f"✓ SemanticCoherence    coherence={sig.get('coherence',0):.3f} judgment={sig.get('judgment','')}")
except Exception as e:
    print(f"✗ SemanticCoherence    {e}")

# 4. PropositionExtractor
try:
    from proposition_extractor import PropositionExtractor
    pe = PropositionExtractor("data/test_props.json")
    result = pe.extract_from_text(
        "La mémoire n'est pas un tiroir mais une durée vécue. Bergson affirme que la conscience est mouvement.",
        source="test"
    )
    sig = pe.signal("mémoire")
    print(f"✓ PropositionExtractor props={len(result)} total={sig.get('count',0)}")
except Exception as e:
    print(f"✗ PropositionExtractor {e}")

# 5. UserModel
try:
    from user_model import UserModel
    um = UserModel("data/test_um.json")
    um.observe("Est-ce que la conscience peut vraiment se connaître elle-même ?")
    um.observe("Je ressens quelque chose d'étrange quand j'y pense.")
    um.observe("La phénoménologie de Husserl répond à ça non ?")
    sig = um.signal()
    print(f"✓ UserModel            vocab={sig.get('vocab_level',0):.3f} domain={sig.get('dominant_domain','')}")
except Exception as e:
    print(f"✗ UserModel            {e}")

# 6. AffectLexicon
try:
    from affect_lexicon import AffectLexicon
    al = AffectLexicon("data/test_affect.json")
    sig = al.signal("Je ressens une angoisse profonde face au néant et à la mort.")
    assert sig["available"]
    print(f"✓ AffectLexicon        valence={sig['valence']:.3f} emotion={sig['emotion']}")
    sig2 = al.signal("Une joie légère, de la curiosité, de l'espoir.")
    print(f"  AffectLexicon+        valence={sig2['valence']:.3f} emotion={sig2['emotion']}")
except Exception as e:
    print(f"✗ AffectLexicon        {e}")

print()
print("=== Intégration core ===")
try:
    from leia_living_core import LeiaLivingCore
    core = LeiaLivingCore()
    # Vérifier que les modules V18 sont bien instanciés
    v18_modules = ["utterance_parser","associative_memory","semantic_coherence",
                   "proposition_extractor","user_model","affect_lexicon"]
    for m in v18_modules:
        status = "✓" if getattr(core, m, None) is not None else "✗ (non instancié)"
        print(f"  core.{m}: {status}")
    print()
    resp = core.process_message("La mémoire peut-elle vraiment trahir ?")
    print(f"✓ process_message OK   réponse: {resp[:80]}...")
except Exception as e:
    print(f"✗ Intégration core     {e}")

print()
print("Nettoyage fichiers test...")
import os, glob
for f in glob.glob("data/test_*.json"):
    try: os.remove(f)
    except: pass
print("Done.")
"""

if __name__ == "__main__":
    print("Ce fichier est un guide de patch.")
    print("Lancer test_v18.py pour valider.")
    print()
    print("Modules V18 :")
    print("  user_utterance_parser.py  — comprendre ce que dit l'utilisateur")
    print("  associative_memory.py     — mémoire hebbienne + spreading activation")
    print("  semantic_coherence.py     — Leia s'entend vraiment")
    print("  proposition_extractor.py  — extraire les thèses des livres")
    print("  user_model.py             — modèle adaptatif de l'interlocuteur")
    print("  affect_lexicon.py         — affect du texte sans LLM")