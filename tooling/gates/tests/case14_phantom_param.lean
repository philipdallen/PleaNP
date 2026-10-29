-- Mock case 14: the #224/#226 phantom-parameter vacuity shape (DEC-029).
--
-- `Withdrawn` reproduces the withdrawn `MachineCode.simulates` field: the field
-- type never mentions the parameter `M`, so it constrains no machine and
-- certifies no behaviour. The syntactic Tier-1 patterns (`True`/`↔ True`/`rfl`/
-- `none`) cannot see it; the parameter-occurrence check (issue #234) must.
--
-- Expected: REVIEW phantom_param for `Withdrawn.simulates` (parameter `M` never
-- occurs in the field type).
--
-- `Clean` is the control: every field type mentions the parameter `M`.

namespace PleaNP.Mock

structure Withdrawn (M : Nat) where
  code : Nat
  simulates : Nat → Nat

structure Clean (M : Nat) where
  simulates : ∀ n : Nat, n = M → n = M

end PleaNP.Mock
