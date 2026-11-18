import tempfile
import unittest
from pathlib import Path
from character_ranking import DEFAULT_MAPPING, EXPECTED_COLUMNS, SOURCE_NAME, build_payload, get_character_rank, load_base_id_mapping, load_stack_rank, rank_characters

def tsv(rows):
    lines=["\t".join(EXPECTED_COLUMNS)]
    lines.extend("\t".join(str(v) for v in row) for row in rows)
    return "\n".join(lines)+"\n"

def row(rank,name,final_tier,base_tier=None,synergy=0,omicron=0):
    values={"Rank":rank,"Character":name,"Sort Score":"5.00","SubSort Score":"12.1000","Final Tier":final_tier,"Base Tier":base_tier if base_tier is not None else final_tier,"Synergy Enhancement":synergy,"Omicron Boost":omicron,"Omicron Synergy Boost":0,"Relic Gear Level":"13.3","Ability Score":0}
    return [values[c] for c in EXPECTED_COLUMNS]

class StackRankImportTests(unittest.TestCase):
    def test_import_preserves_rank_and_keeps_tier_as_audit_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"stack.tsv"
            path.write_text(tsv([row(1,"A",18),row(2,"B",2,8,3),row(3,"C",5,5)]),encoding="utf-8")
            data=load_stack_rank(path)
        self.assertEqual([x["character"] for x in data],["A","B","C"])
        self.assertEqual(data[1]["rank"],2)
        self.assertEqual(data[1]["final_tier"],2)
        self.assertNotIn("importance_score",data[1])


    def test_primary_sort_is_source_rank_only(self):
        rows=[{"character":"B","rank":1,"final_tier":19},{"character":"A","rank":9,"final_tier":2},{"character":"C","rank":3,"final_tier":1}]
        self.assertEqual([x["character"] for x in rank_characters(rows)],["B","C","A"])

    def test_lookup_accepts_display_name_and_base_id(self):
        item={"character":"Grogu & Anzellans","base_id":"GOPHERANTS","rank":270}
        self.assertEqual(get_character_rank([item],"grogu & anzellans")["rank"],270)
        self.assertEqual(get_character_rank([item],"gopherants")["rank"],270)

    def test_rejects_duplicate_names_and_invalid_tiers(self):
        for rows in ([row(1,"A",2),row(2,"a",3)],[row(1,"A",20)]):
            with self.subTest(rows=rows),tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/"bad.tsv"; path.write_text(tsv(rows),encoding="utf-8")
                with self.assertRaises(ValueError): load_stack_rank(path)

    def test_rejects_non_contiguous_rank_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"gap.tsv"
            path.write_text(tsv([row(1,"A",2),row(3,"B",5)]),encoding="utf-8")
            with self.assertRaises(ValueError): load_stack_rank(path)

    def test_mapping_has_315_unique_ids_and_names(self):
        mapping=load_base_id_mapping(DEFAULT_MAPPING)
        self.assertEqual(len(mapping),315)
        self.assertEqual(len({x["base_id"] for x in mapping.values()}),315)
        expected={"the ronin":"THERONIN","third sister":"THIRDSISTER","taron malicos":"TARONMALICOS","dark trooper moff gideon":"MOFFGIDEONS3","jaxxon":"JAXXON"}
        for name,base_id in expected.items(): self.assertEqual(mapping[name]["base_id"],base_id)

    def test_repository_snapshot_maps_all_315_characters(self):
        root=Path(__file__).resolve().parents[1]
        data=load_stack_rank(root/"data"/"stack_rank.tsv",DEFAULT_MAPPING)
        self.assertEqual(len(data),315); self.assertEqual(len({x["base_id"] for x in data}),315)
        self.assertEqual(data[0]["character"],"Rey"); self.assertEqual(data[0]["base_id"],"GLREY")
        self.assertEqual(get_character_rank(data,"Ben Solo")["base_id"],"BENSOLO")
        self.assertEqual(get_character_rank(data,"Grogu & Anzellans")["base_id"],"GOPHERANTS")

    def test_generated_payload_contains_rank_method_and_base_ids(self):
        snapshot=Path(__file__).resolve().parents[1]/"data"/"stack_rank.tsv"
        payload=build_payload(snapshot)
        self.assertEqual(payload["source"],SOURCE_NAME); self.assertEqual(payload["record_count"],315)
        self.assertEqual(payload["schema_version"],4)
        self.assertEqual(payload["method"]["primary_field"],"rank")
        self.assertTrue(all(x["source"]==SOURCE_NAME and x["base_id"] for x in payload["characters"]))

if __name__=="__main__": unittest.main()
